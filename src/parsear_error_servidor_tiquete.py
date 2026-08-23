"""Réplica de app/(app)/facturas/tiquetes/nueva/_lib/parsear-error-servidor.ts
— mismo mecanismo de matching por substrings que parsear_error_servidor.py
(factura), pero con su propio mapeo paso↔campo porque el wizard de Tiquete
tiene 3 pasos en vez de 4: acá "medioPago" es un campo del paso 1 (un solo
medio de pago), y no existe paso de otros cargos."""

from estado_factura import ErrorWizard


def parsear_error_servidor_tiquete(status: int, mensaje: str) -> ErrorWizard:
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
    if "mediopago" in texto or "medio de pago" in texto:
        return ErrorWizard(paso=1, campo="medio_pago", mensaje=mensaje)
    if "moneda" in texto:
        return ErrorWizard(paso=1, campo="moneda", mensaje=mensaje)
    if "tipocambio" in texto or "tipo de cambio" in texto:
        return ErrorWizard(paso=1, campo="tipo_cambio", mensaje=mensaje)
    if any(
        s in texto
        for s in ("lineas[", "línea", "productoid", "cantidad", "preciounitario", "exoneracion")
    ):
        return ErrorWizard(paso=2, campo=None, mensaje=mensaje)

    return ErrorWizard(paso=1, campo=None, mensaje=mensaje)
