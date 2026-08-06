from typing import Callable

import flet as ft

from api.cabys import CabysResultado, buscar_cabys
from ui.componentes.buscador_remoto import construir_buscador_remoto


def _renderizar(item: CabysResultado) -> str:
    return f"{item.codigo_formateado} — {item.descripcion} ({item.impuesto}%)"


def construir_buscador_cabys(
    page: ft.Page,
    al_seleccionar: Callable[[CabysResultado], None],
    valor_inicial: str = "",
) -> ft.Column:
    return construir_buscador_remoto(
        page,
        etiqueta="Código CABYS",
        buscar=buscar_cabys,
        renderizar_opcion=_renderizar,
        al_seleccionar=al_seleccionar,
        valor_inicial=valor_inicial,
        pista="Buscá por descripción o código (mínimo 3 caracteres)",
    )
