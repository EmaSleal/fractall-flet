from typing import Optional

import httpx

_URL_HACIENDA_TIPO_CAMBIO = "https://api.hacienda.go.cr/indicadores/tc/dolar"


async def obtener_tipo_cambio_dolar() -> Optional[float]:
    """No golpea nuestro backend — es la misma API pública de Hacienda que
    usa fractall-frontend (vía su propio proxy `/api/tipo-cambio`, cacheado
    1h). No bloqueante: si falla, el campo de tipo de cambio del wizard
    queda igual editable a mano."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as cliente:
            respuesta = await cliente.get(_URL_HACIENDA_TIPO_CAMBIO)
        if respuesta.status_code != 200:
            return None
        datos = respuesta.json()
        return float(datos["venta"]["valor"])
    except (httpx.HTTPError, KeyError, ValueError, TypeError):
        return None
