"""Estado del wizard de creación de Nota de Crédito Electrónica — equivalente
al useReducer de fractall-frontend (facturas/[id]/nota-credito/nueva/reducer.ts).
Es un wizard de 3 pasos (Motivo, Líneas, Confirmación): igual que Nota de
Débito, NO hay paso de selección de cliente — una NC siempre referencia una
Factura Electrónica origen ya ACEPTADA y hereda su cliente sin poder
cambiarlo. La diferencia real con ND está en el paso de líneas: acá NO se
arman líneas nuevas desde el catálogo de productos, se muestran TODAS las
líneas de la factura origen, precargadas y de solo-mostrar-datos, cada una
con un checkbox de selección (arranca en False) y una cantidad a acreditar
editable (arranca precargada con la cantidad original de esa línea). No hay
tope de monto validado acá — el backend lo valida server-side contra el
saldo disponible de la factura origen (409 MontoNotaCreditoExcedeOrigenException,
ver parsear_error_servidor_nota_credito.py)."""

from dataclasses import dataclass
from typing import Optional

from estado_factura import ErrorWizard

__all__ = [
    "ErrorWizard",
    "LineaNcSeleccionable",
    "EstadoNotaCredito",
    "lineas_seleccionables_desde_factura",
    "calcular_subtotal_acreditar",
    "calcular_iva_acreditar",
    "calcular_subtotal_total_acreditar",
    "calcular_iva_total_acreditar",
    "calcular_total_acreditar",
]


@dataclass
class LineaNcSeleccionable:
    linea_factura_origen_id: str
    numero_linea: int
    codigo_cabys_aplicado: Optional[str]
    unidad_medida_comercial: Optional[str]
    cantidad_origen: float
    precio_unitario: float
    subtotal_origen: float
    porcentaje_impuesto_aplicado: float
    seleccionada: bool = False
    cantidad_acreditar: float = 0.0


def lineas_seleccionables_desde_factura(lineas_origen: list) -> list[LineaNcSeleccionable]:
    """`lineas_origen` es `FacturaDetalle.lineas` (list[LineaFactura] de
    api/facturas.py) — se recibe sin tipar para no acoplar este módulo de
    estado puro a la capa de API; el mapeo es 1 a 1 por campo."""
    return [
        LineaNcSeleccionable(
            linea_factura_origen_id=linea.id,
            numero_linea=linea.numero_linea,
            codigo_cabys_aplicado=linea.codigo_cabys_aplicado,
            unidad_medida_comercial=linea.unidad_medida_comercial,
            cantidad_origen=linea.cantidad,
            precio_unitario=linea.precio_unitario,
            subtotal_origen=linea.subtotal,
            porcentaje_impuesto_aplicado=linea.porcentaje_impuesto_aplicado,
            seleccionada=False,
            cantidad_acreditar=linea.cantidad,
        )
        for linea in lineas_origen
    ]


class EstadoNotaCredito:
    def __init__(
        self,
        factura_origen_id: str,
        factura_origen_consecutivo: str,
        cliente_nombre: str,
        lineas: list[LineaNcSeleccionable],
        moneda: str = "CRC",
    ) -> None:
        self.paso: int = 1
        self.factura_origen_id: str = factura_origen_id
        self.factura_origen_consecutivo: str = factura_origen_consecutivo
        self.cliente_nombre: str = cliente_nombre
        self.moneda: str = moneda
        # Paso 1 — Motivo
        self.codigo_referencia: str = ""
        self.codigo_referencia_otro: str = ""
        self.razon: str = ""
        # Paso 2 — Líneas: todas las de la factura origen, fijas
        self.lineas: list[LineaNcSeleccionable] = lineas
        # Cross-cutting
        self.error_servidor: Optional[ErrorWizard] = None

    def establecer_codigo_referencia(self, codigo: str) -> None:
        self.codigo_referencia = codigo
        if codigo != "99":
            self.codigo_referencia_otro = ""

    def alternar_seleccion_linea(self, indice: int) -> None:
        linea = self.lineas[indice]
        linea.seleccionada = not linea.seleccionada

    def establecer_cantidad_acreditar(self, indice: int, cantidad: float) -> None:
        self.lineas[indice].cantidad_acreditar = cantidad

    def a_cuerpo_creacion(self) -> dict:
        cuerpo: dict = {
            "facturaReferenciaId": self.factura_origen_id,
            "codigoReferencia": self.codigo_referencia,
            "lineas": [
                {
                    "lineaFacturaOrigenId": linea.linea_factura_origen_id,
                    "cantidad": linea.cantidad_acreditar,
                }
                for linea in self.lineas
                if linea.seleccionada
            ],
        }
        if self.codigo_referencia == "99" and self.codigo_referencia_otro.strip():
            cuerpo["codigoReferenciaOtro"] = self.codigo_referencia_otro.strip()
        if self.razon.strip():
            cuerpo["razon"] = self.razon.strip()
        return cuerpo


# ---------------------------------------------------------------------------
# Cálculo — estimaciones de línea, portadas de reducer.ts. El backend es la
# fuente de verdad final: esto es solo para mostrarle al usuario una
# estimación en la UI antes de confirmar.
# ---------------------------------------------------------------------------


def calcular_subtotal_acreditar(linea: LineaNcSeleccionable) -> float:
    if linea.cantidad_origen <= 0:
        return 0.0
    return linea.subtotal_origen * (linea.cantidad_acreditar / linea.cantidad_origen)


def calcular_iva_acreditar(linea: LineaNcSeleccionable) -> float:
    return calcular_subtotal_acreditar(linea) * (linea.porcentaje_impuesto_aplicado / 100)


def calcular_subtotal_total_acreditar(lineas: list[LineaNcSeleccionable]) -> float:
    return sum(calcular_subtotal_acreditar(l) for l in lineas if l.seleccionada)


def calcular_iva_total_acreditar(lineas: list[LineaNcSeleccionable]) -> float:
    return sum(calcular_iva_acreditar(l) for l in lineas if l.seleccionada)


def calcular_total_acreditar(lineas: list[LineaNcSeleccionable]) -> float:
    return calcular_subtotal_total_acreditar(lineas) + calcular_iva_total_acreditar(lineas)
