"""Réplica de app/(app)/facturas/[id]/poll-estado-factura.tsx — el POST de
creación (Factura, Tiquete, y a futuro NC/ND) sigue el patrón "2 llamadas":
la respuesta HTTP inicial refleja el estado justo después de crear la fila
(GENERADO), no el resultado final de Hacienda. Sin este polling, la página
de detalle se queda mostrando ENVIADO/GENERADO indefinidamente hasta que el
usuario recargue a mano.

Genérico por tipo de comprobante a propósito: no importa FacturaDetalle ni
ningún estado de wizard, solo necesita una función `consultar` y un
`extraer_estado` — así lo puede usar tanto el detalle de Factura como el de
Tiquete (y mañana NC/ND) sin duplicar el bucle."""

import asyncio
from typing import Awaitable, Callable, Optional, TypeVar

from api.cliente import ApiFallo

T = TypeVar("T")

ESTADOS_NO_TERMINALES = {"GENERADO", "FIRMADO", "ENVIADO"}
INTERVALO_SEGUNDOS = 3
MAX_INTENTOS = 20  # ~60s — el job de reconciliación del backend es el respaldo si Hacienda tarda más


async def esperar_estado_final(
    consultar: Callable[[], Awaitable],
    estado_inicial: str,
    extraer_estado: Callable[[T], str],
) -> Optional[T]:
    """Devuelve el dato recién consultado en cuanto su estado deja de ser
    no-terminal, o None si el estado inicial ya era terminal, si se agotan
    los intentos, o si alguna consulta falla."""
    if estado_inicial not in ESTADOS_NO_TERMINALES:
        return None

    for _ in range(MAX_INTENTOS):
        await asyncio.sleep(INTERVALO_SEGUNDOS)
        resultado = await consultar()
        if isinstance(resultado, ApiFallo):
            return None
        datos = resultado.datos
        if datos is None:
            return None
        if extraer_estado(datos) not in ESTADOS_NO_TERMINALES:
            return datos

    return None
