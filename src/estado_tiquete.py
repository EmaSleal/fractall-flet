"""Estado del wizard de creación de Tiquete Electrónico — equivalente al
useReducer de fractall-frontend (facturas/tiquetes/nueva/reducer.ts). Es un
wizard de 3 pasos (Cliente, Líneas, Confirmación) en vez de los 4 de
Factura: no hay paso de medios de pago múltiples (POST /tiquetes solo
acepta un `medioPago` único) ni de otros cargos, y el cliente es opcional
(venta de mostrador, sin receptor identificado)."""

from typing import Optional

from estado_factura import ErrorWizard, ExoneracionVigenteItem, LineaWizard, cuerpo_linea_wizard

__all__ = ["ErrorWizard", "ExoneracionVigenteItem", "LineaWizard", "EstadoTiquete"]


class EstadoTiquete:
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
        self.medio_pago: str = "01"
        self.moneda: str = "CRC"
        self.tipo_cambio: float = 1.0
        # Paso 2
        self.lineas: list[LineaWizard] = [LineaWizard()]
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

    def quitar_cliente(self) -> None:
        self.cliente_id = None
        self.cliente_nombre = None
        self.cliente_identificacion = None
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
            "condicionVenta": self.condicion_venta,
            "medioPago": self.medio_pago,
            "moneda": self.moneda,
            "tipoCambio": 1.0 if self.moneda == "CRC" else self.tipo_cambio,
            "lineas": [cuerpo_linea_wizard(linea) for linea in self.lineas],
        }
        if self.cliente_id:
            cuerpo["clienteId"] = self.cliente_id
        if self.condicion_venta == "02" and self.plazo_credito:
            cuerpo["plazoCredito"] = self.plazo_credito
        if self.condicion_venta == "99" and self.condicion_venta_otros.strip():
            cuerpo["condicionVentaOtros"] = self.condicion_venta_otros.strip()
        return cuerpo
