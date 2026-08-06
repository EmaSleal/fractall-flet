"""Validación por paso del wizard — réplica de los schemas Zod
(schemaPaso1/2/3) de fractall-frontend. Cada función devuelve un dict
{clave_campo: mensaje} — vacío significa "válido"."""

from typing import Optional

from estado_factura import EstadoFactura, MedioPagoWizard, OtroCargoWizard


def validar_paso1(estado: EstadoFactura) -> dict[str, str]:
    errores: dict[str, str] = {}
    if not estado.cliente_id:
        errores["cliente_id"] = "Seleccioná un cliente válido"
    if estado.condicion_venta == "02" and not estado.plazo_credito:
        errores["plazo_credito"] = "Requerido para condición de venta a crédito"
    if estado.condicion_venta == "99" and not estado.condicion_venta_otros.strip():
        errores["condicion_venta_otros"] = "Requerido para condición de venta \"Otros\""
    if estado.moneda == "USD" and not (400 <= estado.tipo_cambio <= 700):
        errores["tipo_cambio"] = "Fuera del rango esperado: ₡400 – ₡700 por USD"
    return errores


def validar_paso2(estado: EstadoFactura) -> dict[str, str]:
    errores: dict[str, str] = {}
    if not estado.lineas:
        errores["lineas"] = "Agregá al menos una línea"
        return errores
    for i, linea in enumerate(estado.lineas):
        if not linea.producto_id:
            errores[f"lineas.{i}.producto_id"] = "Elegí un producto"
        if linea.cantidad <= 0:
            errores[f"lineas.{i}.cantidad"] = "Debe ser mayor a 0"
        if linea.precio_unitario < 0:
            errores[f"lineas.{i}.precio_unitario"] = "No puede ser negativo"
    return errores


def validar_medio_pago(medio: MedioPagoWizard) -> Optional[str]:
    if not medio.tipo_medio_pago:
        return "Seleccioná un tipo"
    if medio.tipo_medio_pago == "99" and len(medio.medio_pago_otros.strip()) < 3:
        return 'Requerido cuando el tipo es "99 — Otros" (mínimo 3 caracteres)'
    return None


def validar_otro_cargo(cargo: OtroCargoWizard) -> Optional[str]:
    if not cargo.tipo_documento_oc:
        return "Seleccioná un tipo"
    if cargo.tipo_documento_oc == "99" and not cargo.tipo_documento_otros.strip():
        return 'Requerido cuando el tipo es "99 — Otros"'
    return None


def validar_paso3(estado: EstadoFactura) -> dict[str, str]:
    errores: dict[str, str] = {}
    if not estado.medios_pago:
        errores["medios_pago"] = "Agregá al menos un medio de pago"
    elif len(estado.medios_pago) > 4:
        errores["medios_pago"] = "Máximo 4 medios de pago"

    for i, medio in enumerate(estado.medios_pago):
        error = validar_medio_pago(medio)
        if error:
            errores[f"medios_pago.{i}"] = error

    for i, cargo in enumerate(estado.otros_cargos):
        error = validar_otro_cargo(cargo)
        if error:
            errores[f"otros_cargos.{i}"] = error

    return errores
