from typing import Callable

import flet as ft

from api.unidades_medida import UnidadMedida
from ui.componentes.combobox_local import construir_combobox_local


def _texto_busqueda(item: UnidadMedida) -> str:
    return f"{item.codigo} {item.descripcion}"


def _renderizar(item: UnidadMedida) -> str:
    return f"{item.codigo} — {item.descripcion}"


def construir_selector_unidad_medida(
    unidades: list[UnidadMedida],
    al_seleccionar: Callable[[UnidadMedida], None],
    valor_inicial: str = "",
) -> ft.SearchBar:
    return construir_combobox_local(
        etiqueta="Unidad de medida (Hacienda)",
        items=unidades,
        texto_busqueda=_texto_busqueda,
        renderizar_opcion=_renderizar,
        al_seleccionar=al_seleccionar,
        valor_inicial=valor_inicial,
        pista="Filtrá por código o descripción",
    )
