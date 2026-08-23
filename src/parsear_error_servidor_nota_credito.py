"""Réplica de app/(app)/facturas/[id]/nota-credito/nueva/_lib/parsear-error-servidor.ts
— a diferencia del parser de ND, acá SÍ se conoce el texto exacto de cada
excepción de dominio del backend (confirmado leyendo
fractall/facturacion/servicio/*Exception.java), así que el matching por
substring es específico y no heurístico a ciegas:
- FacturaOrigenNoAceptadaException (409): "no está en estado ACEPTADO"
- MontoNotaCreditoExcedeOrigenException (409): "excede el total de la
  factura origen" — el tope de monto que el cliente NO valida, se muestra
  tal cual venga del backend en el paso 2 (Líneas).
- CantidadAcreditadaExcedeOrigenException (400): "excede la cantidad de la
  línea origen"
- LineaOrigenNoPerteneceAFacturaException (400): "no pertenece a la factura"
"""

from estado_factura import ErrorWizard


def parsear_error_servidor_nota_credito(status: int, mensaje: str) -> ErrorWizard:
    texto = mensaje.lower()

    if status == 404:
        return ErrorWizard(
            paso=1,
            campo=None,
            mensaje="La factura origen no se encontró. Verificá que siga existiendo.",
        )

    if status == 409:
        if "no está en estado aceptado" in texto:
            return ErrorWizard(paso=1, campo=None, mensaje=mensaje)
        if "excede el total de la factura origen" in texto:
            return ErrorWizard(paso=2, campo=None, mensaje=mensaje)
        return ErrorWizard(paso=1, campo=None, mensaje=mensaje)

    if "excede la cantidad de la línea" in texto or "no pertenece a la factura" in texto:
        return ErrorWizard(paso=2, campo=None, mensaje=mensaje)
    if "codigoreferencia" in texto or "código de referencia" in texto:
        return ErrorWizard(paso=1, campo="codigo_referencia", mensaje=mensaje)
    if "razon" in texto or "razón" in texto:
        return ErrorWizard(paso=1, campo="razon", mensaje=mensaje)
    if any(s in texto for s in ("lineas[", "línea", "cantidad")):
        return ErrorWizard(paso=2, campo=None, mensaje=mensaje)

    return ErrorWizard(paso=1, campo=None, mensaje=mensaje)
