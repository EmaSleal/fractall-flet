from types import SimpleNamespace

from ui.componentes.combobox_local import construir_combobox_local


def _construir(monkeypatch, items, valor_inicial=""):
    seleccionados = []
    llamadas = {"open_view": 0, "close_view": []}

    def _al_seleccionar(item):
        seleccionados.append(item)

    barra = construir_combobox_local(
        etiqueta="Unidad",
        items=items,
        texto_busqueda=lambda i: f"{i[0]} {i[1]}",
        renderizar_opcion=lambda i: f"{i[0]} — {i[1]}",
        al_seleccionar=_al_seleccionar,
        valor_inicial=valor_inicial,
    )

    async def _open_view_falso():
        llamadas["open_view"] += 1

    async def _close_view_falso(text=None):
        llamadas["close_view"].append(text)

    monkeypatch.setattr(barra, "open_view", _open_view_falso)
    monkeypatch.setattr(barra, "close_view", _close_view_falso)
    monkeypatch.setattr(barra, "update", lambda: None)

    return barra, seleccionados, llamadas


def test_arranca_con_todos_los_items_cargados():
    items = [("Sp", "Servicios profesionales"), ("Unid", "Unidad")]
    barra = construir_combobox_local(
        etiqueta="Unidad",
        items=items,
        texto_busqueda=lambda i: f"{i[0]} {i[1]}",
        renderizar_opcion=lambda i: f"{i[0]} — {i[1]}",
        al_seleccionar=lambda item: None,
    )

    assert [c.title.value for c in barra.controls] == [
        "Sp — Servicios profesionales",
        "Unid — Unidad",
    ]


async def test_tap_muestra_todos_los_items_sin_importar_el_texto(monkeypatch):
    """Regresión: al clickear el campo vacío (o con un valor precargado en
    edición) tiene que listar todo el catálogo, no solo lo que matchee el
    texto actual — eso es justo lo que AutoComplete no permitía hacer."""
    items = [("Sp", "Servicios profesionales"), ("Unid", "Unidad")]
    barra, _seleccionados, llamadas = _construir(
        monkeypatch, items, valor_inicial="Sp — Servicios profesionales"
    )
    barra.controls = []  # simula que on_change ya había acotado la lista antes

    await barra.on_tap(None)

    assert llamadas["open_view"] == 1
    assert len(barra.controls) == 2


async def test_filtra_localmente_por_texto(monkeypatch):
    items = [("Sp", "Servicios profesionales"), ("Unid", "Unidad")]
    barra, _seleccionados, _llamadas = _construir(monkeypatch, items)
    barra.value = "prof"

    barra.on_change(SimpleNamespace(control=barra))

    assert len(barra.controls) == 1
    assert barra.controls[0].title.value == "Sp — Servicios profesionales"


async def test_elegir_opcion_llama_al_seleccionar_y_cierra_la_vista(monkeypatch):
    items = [("Sp", "Servicios profesionales")]
    barra, seleccionados, llamadas = _construir(monkeypatch, items)

    await barra.controls[0].on_click(None)

    assert seleccionados == [("Sp", "Servicios profesionales")]
    assert llamadas["close_view"] == ["Sp — Servicios profesionales"]
