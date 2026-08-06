"""Réplica exacta de app/(app)/facturas/nueva/_lib/parsear-error-servidor.ts
— mapea un error del backend a qué paso del wizard corregir. El backend
concatena errores de campo en un solo string ("campo: msg; campo2: msg2",
según la descripción de MensajeResponse en el openapi), así que esto hace
matching de substrings sobre ese string plano, en un orden de prioridad
fijo — no es JSON estructurado por campo."""

from estado_factura import ErrorWizard


def parsear_error_servidor(status: int, mensaje: str) -> ErrorWizard:
    if status == 404:
        return ErrorWizard(
            paso=1,
            campo=None,
            mensaje="No se encontró el cliente o alguno de los productos seleccionados.",
        )
    if status == 503:
        return ErrorWizard(
            paso=1,
            campo=None,
            mensaje="La configuración de Hacienda de la empresa está incompleta.",
        )

    texto = mensaje.lower()

    if "clienteid" in texto or "cliente" in texto:
        return ErrorWizard(paso=1, campo="cliente_id", mensaje=mensaje)
    if "condicionventa" in texto or "condición de venta" in texto:
        return ErrorWizard(paso=1, campo="condicion_venta", mensaje=mensaje)
    if "plazocredito" in texto or "plazo" in texto:
        return ErrorWizard(paso=1, campo="plazo_credito", mensaje=mensaje)
    if "moneda" in texto:
        return ErrorWizard(paso=1, campo="moneda", mensaje=mensaje)
    if "tipocambio" in texto or "tipo de cambio" in texto:
        return ErrorWizard(paso=1, campo="tipo_cambio", mensaje=mensaje)
    if any(
        s in texto
        for s in ("lineas[", "línea", "productoid", "cantidad", "preciounitario", "exoneracion")
    ):
        return ErrorWizard(paso=2, campo=None, mensaje=mensaje)
    if any(
        s in texto
        for s in ("mediospago", "medio de pago", "totalmedio", "otroscargos", "cargo")
    ):
        return ErrorWizard(paso=3, campo=None, mensaje=mensaje)

    return ErrorWizard(paso=1, campo=None, mensaje=mensaje)
