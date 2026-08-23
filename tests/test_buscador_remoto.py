from types import SimpleNamespace

from api.cliente import ApiExito, ApiFallo
from api.errores import ErrorApi
from diseno import tokens
from ui.componentes.buscador_remoto import construir_buscador_remoto


async def _sin_espera(_segundos):
    return None


def _construir(monkeypatch, resultado, *, al_seleccionar=None):
    llamadas = []
    seleccionados = []

    async def _buscar(consulta):
        llamadas.append(consulta)
        return resultado

    page = SimpleNamespace(update=lambda: None, navigate=lambda *a, **k: None)

    barra = construir_buscador_remoto(
        page,
        etiqueta="Cliente",
        buscar=_buscar,
        renderizar_opcion=lambda item: item,
        al_seleccionar=al_seleccionar or seleccionados.append,
    )

    async def _open_view_falso():
        pass

    async def _close_view_falso(text=None):
        pass

    monkeypatch.setattr(barra, "open_view", _open_view_falso)
    monkeypatch.setattr(barra, "close_view", _close_view_falso)
    monkeypatch.setattr(barra, "update", lambda: None)
    monkeypatch.setattr("asyncio.sleep", _sin_espera)

    return barra, llamadas, seleccionados


def test_hint_por_defecto_es_buscar():
    page = SimpleNamespace(update=lambda: None, navigate=lambda *a, **k: None)
    barra = construir_buscador_remoto(
        page,
        etiqueta="Cliente",
        buscar=lambda consulta: None,
        renderizar_opcion=lambda item: item,
        al_seleccionar=lambda item: None,
    )

    assert barra.view_hint_text == "Buscar..."


async def test_abrir_dispara_busqueda_con_consulta_vacia(monkeypatch):
    barra, llamadas, _seleccionados = _construir(monkeypatch, ApiExito(datos=["Ana", "Beto"]))

    await barra.on_tap(None)

    assert llamadas == [""]
    assert [c.title.value for c in barra.controls] == ["Ana", "Beto"]


async def test_escribir_menos_de_tres_caracteres_igual_busca(monkeypatch):
    barra, llamadas, _seleccionados = _construir(monkeypatch, ApiExito(datos=["Ana"]))
    barra.value = "an"

    await barra.on_change(SimpleNamespace(control=barra))

    assert llamadas == ["an"]
    assert [c.title.value for c in barra.controls] == ["Ana"]


async def test_sin_resultados_muestra_mensaje_no_seleccionable(monkeypatch):
    barra, _llamadas, _seleccionados = _construir(monkeypatch, ApiExito(datos=[]))

    await barra.on_tap(None)

    assert len(barra.controls) == 1
    assert barra.controls[0].title.value == "Sin resultados"
    assert barra.controls[0].disabled is True


async def test_error_de_red_se_distingue_de_sin_resultados(monkeypatch):
    barra, _llamadas, _seleccionados = _construir(
        monkeypatch, ApiFallo(error=ErrorApi(mensaje="Error al buscar clientes.", status=500))
    )

    await barra.on_tap(None)

    fila = barra.controls[0]
    assert fila.title.value == "Error al buscar clientes."
    assert fila.disabled is True
    assert fila.title.color == tokens.ESTADO_RECHAZADO  # distinto del gris neutro


async def test_elegir_opcion_llama_al_seleccionar_y_cierra_la_vista(monkeypatch):
    barra, _llamadas, seleccionados = _construir(monkeypatch, ApiExito(datos=["Ana"]))

    await barra.on_tap(None)
    await barra.controls[0].on_click(None)

    assert seleccionados == ["Ana"]
