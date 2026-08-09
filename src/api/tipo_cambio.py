from typing import Optional

from .cliente import ApiFallo
from .cliente_autenticado import peticion_autenticada


async def obtener_tipo_cambio_dolar() -> Optional[float]:
    """GET /catalogo/tipo-cambio/dolar — el backend cachea y autentica la
    consulta a Hacienda, mismo patrón que el resto de /catalogo/* (antes
    este módulo le pegaba directo a la API pública de Hacienda). No
    bloqueante: si falla, el campo de tipo de cambio del wizard queda igual
    editable a mano."""
    resultado = await peticion_autenticada("GET", "/catalogo/tipo-cambio/dolar")
    if isinstance(resultado, ApiFallo):
        return None
    try:
        return float(resultado.datos["venta"]["valor"])
    except (KeyError, ValueError, TypeError):
        return None
