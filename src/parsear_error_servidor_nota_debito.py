"""Réplica de app/(app)/facturas/[id]/nota-debito/nueva/_lib/parsear-error-servidor.ts
— mismo mecanismo de matching por substrings que
parsear_error_servidor_tiquete.py, con el mapeo paso↔campo propio de ND:
"codigoReferencia"/"razon" son del paso 1 (Motivo). El 409 NO se interpreta
por texto — hay al menos tres excepciones de dominio distintas que
responden 409 con el mismo shape `{mensaje}` (factura origen que dejó de
estar ACEPTADO entre la carga de la página y el envío, comprobante no
reenviable, etc.) — se muestra tal cual en el paso 1."""

from estado_factura import ErrorWizard


def parsear_error_servidor_nota_debito(status: int, mensaje: str) -> ErrorWizard:
    if status == 409:
        return ErrorWizard(paso=1, campo=None, mensaje=mensaje)
    if status == 404:
        return ErrorWizard(
            paso=1,
            campo=None,
            mensaje="Un recurso referenciado no se encontró. Verificá que la factura "
            "origen y los productos sigan existiendo.",
        )

    texto = mensaje.lower()

    if "codigoreferencia" in texto or "código de referencia" in texto:
        return ErrorWizard(paso=1, campo="codigo_referencia", mensaje=mensaje)
    if "razon" in texto or "razón" in texto:
        return ErrorWizard(paso=1, campo="razon", mensaje=mensaje)
    if any(
        s in texto
        for s in ("lineas[", "línea", "productoid", "cantidad", "preciounitario", "exoneracion")
    ):
        return ErrorWizard(paso=2, campo=None, mensaje=mensaje)

    return ErrorWizard(paso=1, campo=None, mensaje=mensaje)
