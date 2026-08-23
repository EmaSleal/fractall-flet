"""Estado del wizard de creación de Nota de Débito Electrónica — equivalente al
useReducer de fractall-frontend (facturas/[id]/nota-debito/nueva/reducer.ts). Es
un wizard de 3 pasos (Motivo, Líneas, Confirmación): a diferencia de Factura y
Tiquete, acá NO hay paso de selección de cliente — una ND siempre referencia una
Factura Electrónica origen ya ACEPTADA y hereda su cliente sin poder cambiarlo
(el `facturaReferenciaId` es lo que determina el cliente en el backend), así que
el punto de entrada del wizard (ver ui/paginas/facturas/nota_debito/nueva/wizard.py)
ya trae esos datos resueltos al construir el estado."""

from typing import Optional

from estado_factura import ErrorWizard, ExoneracionVigenteItem, LineaWizard, cuerpo_linea_wizard

__all__ = ["ErrorWizard", "ExoneracionVigenteItem", "LineaWizard", "EstadoNotaDebito"]


class EstadoNotaDebito:
    def __init__(
        self,
        factura_origen_id: str,
        factura_origen_consecutivo: str,
        cliente_nombre: str,
        moneda: str = "CRC",
    ) -> None:
        self.paso: int = 1
        self.factura_origen_id: str = factura_origen_id
        self.factura_origen_consecutivo: str = factura_origen_consecutivo
        self.cliente_nombre: str = cliente_nombre
        self.moneda: str = moneda
        self.exoneraciones_vigentes: list[ExoneracionVigenteItem] = []
        # Paso 1 — Motivo
        self.codigo_referencia: str = ""
        self.codigo_referencia_otro: str = ""
        self.razon: str = ""
        # Paso 2 — Líneas
        self.lineas: list[LineaWizard] = [LineaWizard()]
        # Cross-cutting
        self.error_servidor: Optional[ErrorWizard] = None

    def establecer_exoneraciones_vigentes(self, items: list[ExoneracionVigenteItem]) -> None:
        self.exoneraciones_vigentes = items

    def establecer_codigo_referencia(self, codigo: str) -> None:
        self.codigo_referencia = codigo
        if codigo != "99":
            self.codigo_referencia_otro = ""

    def agregar_linea(self) -> None:
        self.lineas.append(LineaWizard())

    def quitar_linea(self, indice: int) -> None:
        if len(self.lineas) <= 1:
            return
        del self.lineas[indice]

    def a_cuerpo_creacion(self) -> dict:
        cuerpo: dict = {
            "facturaReferenciaId": self.factura_origen_id,
            "codigoReferencia": self.codigo_referencia,
            "lineas": [cuerpo_linea_wizard(linea) for linea in self.lineas],
        }
        if self.codigo_referencia == "99" and self.codigo_referencia_otro.strip():
            cuerpo["codigoReferenciaOtro"] = self.codigo_referencia_otro.strip()
        if self.razon.strip():
            cuerpo["razon"] = self.razon.strip()
        return cuerpo
