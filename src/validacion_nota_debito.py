"""Validación por paso del wizard de Nota de Débito — réplica de
schemaPasoMotivo de fractall-frontend
(facturas/[id]/nota-debito/nueva/reducer.ts). No hay tope de monto que
validar acá (a diferencia de Nota de Crédito): el backend no lo exige para
ND y el frontend tampoco lo valida client-side."""

from estado_nota_debito import EstadoNotaDebito
from validacion_factura import validar_paso2  # noqa: F401 — mismo shape de líneas, se reexporta

_LARGO_MAXIMO_RAZON = 180


def validar_paso1(estado: EstadoNotaDebito) -> dict[str, str]:
    errores: dict[str, str] = {}
    if not estado.codigo_referencia:
        errores["codigo_referencia"] = "Seleccioná un código de referencia"
    if estado.codigo_referencia == "99" and not estado.codigo_referencia_otro.strip():
        errores["codigo_referencia_otro"] = 'Requerido cuando el código es "Otros"'
    if len(estado.razon) > _LARGO_MAXIMO_RAZON:
        errores["razon"] = f"Máximo {_LARGO_MAXIMO_RAZON} caracteres"
    return errores
