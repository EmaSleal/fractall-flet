"""Validación por paso del wizard de Tiquete — réplica de schemaPaso1 de
fractall-frontend (facturas/tiquetes/nueva/reducer.ts). A diferencia de
validacion_factura, acá cliente_id NO es obligatorio (venta de mostrador)."""

from estado_tiquete import EstadoTiquete
from validacion_factura import validar_paso2  # noqa: F401 — mismo shape de líneas, se reexporta


def validar_paso1(estado: EstadoTiquete) -> dict[str, str]:
    errores: dict[str, str] = {}
    if estado.condicion_venta == "02" and not estado.plazo_credito:
        errores["plazo_credito"] = "Requerido para condición de venta a crédito"
    if estado.condicion_venta == "99" and not estado.condicion_venta_otros.strip():
        errores["condicion_venta_otros"] = "Requerido para condición de venta \"Otros\""
    if not estado.medio_pago:
        errores["medio_pago"] = "Seleccioná un medio de pago"
    if estado.moneda == "USD" and not (400 <= estado.tipo_cambio <= 700):
        errores["tipo_cambio"] = "Fuera del rango esperado: ₡400 – ₡700 por USD"
    if estado.moneda not in ("CRC", "USD") and estado.tipo_cambio <= 0:
        errores["tipo_cambio"] = "Requerido para monedas distintas de CRC/USD"
    return errores
