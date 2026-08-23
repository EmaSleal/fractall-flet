"""Validación por paso del wizard de Nota de Crédito — réplica de
schemaPasoMotivo/schemaPasoLineas de fractall-frontend
(facturas/[id]/nota-credito/nueva/reducer.ts). El paso 1 (Motivo) es
idéntico al de Nota de Débito, se reexporta directo. El paso 2 es propio de
NC: no hay tope de monto que validar acá (el backend lo valida server-side
contra el saldo disponible de la factura origen, ver
parsear_error_servidor_nota_credito.py) — la regla client-side es solo
"al menos una línea seleccionada" y, por cada seleccionada, cantidad a
acreditar > 0 y <= cantidad facturada de esa línea."""

from estado_nota_credito import EstadoNotaCredito
from validacion_nota_debito import validar_paso1  # noqa: F401 — mismo shape del paso Motivo


def validar_paso2(estado: EstadoNotaCredito) -> dict[str, str]:
    errores: dict[str, str] = {}
    seleccionadas = [linea for linea in estado.lineas if linea.seleccionada]
    if not seleccionadas:
        errores["lineas"] = "Seleccioná al menos una línea para acreditar"
        return errores

    for i, linea in enumerate(estado.lineas):
        if not linea.seleccionada:
            continue
        if not (linea.cantidad_acreditar > 0):
            errores[f"lineas.{i}.cantidad_acreditar"] = "Debe ser mayor a 0"
        elif linea.cantidad_acreditar > linea.cantidad_origen:
            errores[f"lineas.{i}.cantidad_acreditar"] = "No puede exceder la cantidad facturada"

    return errores
