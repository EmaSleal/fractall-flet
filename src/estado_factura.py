"""Estado del wizard de creación de factura — equivalente al useReducer de
fractall-frontend (reducer.ts). Se usa una clase mutable en vez de un
reducer con acciones porque en Python/Flet no hay un dispatch centralizado
que se beneficie de esa indirección; los métodos de esta clase SON las
acciones, y encapsulan las mismas reglas de limpieza de campos
dependientes que tenía el reducer original."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ExoneracionVigenteItem:
    id: str
    descripcion: str


@dataclass
class LineaWizard:
    producto_id: Optional[str] = None
    producto_descripcion: str = ""
    cantidad: float = 1.0
    precio_unitario: float = 0.0
    porcentaje_impuesto: float = 0.0
    descuento_monto: float = 0.0
    descuento_razon: str = ""
    exoneracion_id: Optional[str] = None


@dataclass
class MedioPagoWizard:
    tipo_medio_pago: str = ""
    medio_pago_otros: str = ""
    total_medio_pago: float = 0.0


@dataclass
class OtroCargoWizard:
    tipo_documento_oc: str = ""
    tipo_documento_otros: str = ""
    detalle: str = ""
    monto_cargo: float = 0.0
    nombre_tercero: str = ""
    identificacion_tipo: str = ""
    identificacion_numero: str = ""


@dataclass
class ErrorWizard:
    paso: int
    campo: Optional[str]
    mensaje: str


def _cuerpo_linea(linea: LineaWizard) -> dict:
    item: dict = {
        "productoId": linea.producto_id,
        "cantidad": linea.cantidad,
        "precioUnitario": linea.precio_unitario,
    }
    if linea.exoneracion_id:
        item["exoneracionId"] = linea.exoneracion_id
    if linea.descuento_monto > 0:
        item["descuentos"] = [
            {
                "montoDescuento": linea.descuento_monto,
                "naturalezaDescuento": linea.descuento_razon.strip() or None,
            }
        ]
    return item


def _cuerpo_medio_pago(medio: MedioPagoWizard) -> dict:
    item: dict = {
        "tipoMedioPago": medio.tipo_medio_pago,
        "totalMedioPago": medio.total_medio_pago,
    }
    if medio.tipo_medio_pago == "99":
        item["medioPagoOtros"] = medio.medio_pago_otros.strip()
    return item


def _cuerpo_otro_cargo(cargo: OtroCargoWizard) -> dict:
    item: dict = {
        "tipoDocumentoOc": cargo.tipo_documento_oc,
        "montoCargo": cargo.monto_cargo,
    }
    if cargo.tipo_documento_oc == "99":
        item["tipoDocumentoOtros"] = cargo.tipo_documento_otros.strip()
    if cargo.nombre_tercero.strip():
        item["nombreTercero"] = cargo.nombre_tercero.strip()
    if cargo.detalle.strip():
        item["detalle"] = cargo.detalle.strip()
    if cargo.identificacion_numero.strip():
        item["identificacionTercero"] = {
            "tipo": cargo.identificacion_tipo.strip(),
            "numero": cargo.identificacion_numero.strip(),
        }
    return item


class EstadoFactura:
    def __init__(self) -> None:
        self.paso: int = 1
        # Paso 1
        self.cliente_id: Optional[str] = None
        self.cliente_nombre: Optional[str] = None
        self.cliente_identificacion: Optional[str] = None
        self.exoneraciones_vigentes: list[ExoneracionVigenteItem] = []
        self.condicion_venta: str = "01"
        self.plazo_credito: Optional[int] = None
        self.condicion_venta_otros: str = ""
        self.moneda: str = "CRC"
        self.tipo_cambio: float = 1.0
        # Paso 2
        self.lineas: list[LineaWizard] = [LineaWizard()]
        # Paso 3
        self.medios_pago: list[MedioPagoWizard] = []
        self.otros_cargos: list[OtroCargoWizard] = []
        # Cross-cutting
        self.error_servidor: Optional[ErrorWizard] = None

    def establecer_cliente(
        self, cliente_id: str, cliente_nombre: str, cliente_identificacion: str
    ) -> None:
        self.cliente_id = cliente_id
        self.cliente_nombre = cliente_nombre
        self.cliente_identificacion = cliente_identificacion
        self.exoneraciones_vigentes = []
        for linea in self.lineas:
            linea.exoneracion_id = None

    def establecer_exoneraciones_vigentes(self, items: list[ExoneracionVigenteItem]) -> None:
        self.exoneraciones_vigentes = items

    def establecer_condicion_venta(self, condicion: str) -> None:
        self.condicion_venta = condicion
        if condicion != "02":
            self.plazo_credito = None
        if condicion != "99":
            self.condicion_venta_otros = ""

    def establecer_moneda(self, moneda: str) -> None:
        self.moneda = moneda
        if moneda == "CRC":
            self.tipo_cambio = 1.0

    def agregar_linea(self) -> None:
        self.lineas.append(LineaWizard())

    def quitar_linea(self, indice: int) -> None:
        if len(self.lineas) <= 1:
            return
        del self.lineas[indice]

    def a_cuerpo_creacion(self) -> dict:
        cuerpo: dict = {
            "clienteId": self.cliente_id,
            "condicionVenta": self.condicion_venta,
            "moneda": self.moneda,
            "tipoCambio": 1.0 if self.moneda == "CRC" else self.tipo_cambio,
            "lineas": [_cuerpo_linea(linea) for linea in self.lineas],
        }
        if self.condicion_venta == "02" and self.plazo_credito:
            cuerpo["plazoCredito"] = self.plazo_credito
        if self.condicion_venta == "99" and self.condicion_venta_otros.strip():
            cuerpo["condicionVentaOtros"] = self.condicion_venta_otros.strip()
        if self.medios_pago:
            cuerpo["mediosPago"] = [_cuerpo_medio_pago(m) for m in self.medios_pago]
        if self.otros_cargos:
            cuerpo["otrosCargos"] = [_cuerpo_otro_cargo(c) for c in self.otros_cargos]
        return cuerpo
