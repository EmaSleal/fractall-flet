"""Flet no tiene path params tipo `/clientes/{id}` — las rutas con datos
variables usan query string (`/clientes/detalle?id=...`) y se leen acá,
sin depender de `page.query` (cuyo timing de refresco respecto al evento
`on_route_change` no está garantizado por la doc)."""

from typing import Optional
from urllib.parse import parse_qs, urlparse


def ruta_base(ruta_completa: str) -> str:
    return urlparse(ruta_completa).path


def parametro(ruta_completa: str, clave: str) -> Optional[str]:
    valores = parse_qs(urlparse(ruta_completa).query).get(clave)
    return valores[0] if valores else None
