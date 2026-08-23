from types import SimpleNamespace

from api.cliente import ApiExito
from ui.componentes.buscador_remoto import construir_buscador_remoto


def _construir(monkeypatch, resultado):
    llamadas = []

    async def _buscar(consulta):
        llamadas.append(consulta)
        return resultado

    page = SimpleNamespace(update=lambda: None, navigate=lambda *a, **k: None)

    columna = construir_buscador_remoto(
        page,
        etiqueta="Cliente",
        buscar=_buscar,
        renderizar_opcion=lambda item: item,
        al_seleccionar=lambda item: None,
    )
    campo, texto_estado, resultados = columna.controls
    monkeypatch.setattr("asyncio.sleep", _sin_espera)
    return campo, texto_estado, resultados, llamadas


async def _sin_espera(_segundos):
    return None


def test_hint_por_defecto_es_buscar():
    page = SimpleNamespace(update=lambda: None, navigate=lambda *a, **k: None)
    columna = construir_buscador_remoto(
        page,
        etiqueta="Cliente",
        buscar=lambda consulta: None,
        renderizar_opcion=lambda item: item,
        al_seleccionar=lambda item: None,
    )
    campo = columna.controls[0]

    assert campo.hint_text == "Buscar..."


async def test_enfocar_dispara_busqueda_con_consulta_vacia(monkeypatch):
    campo, _texto_estado, resultados, llamadas = _construir(
        monkeypatch, ApiExito(datos=["Ana", "Beto"])
    )

    await campo.on_focus(None)

    assert llamadas == [""]
    assert resultados.visible is True
    assert [c.content for c in resultados.controls] == ["Ana", "Beto"]


async def test_enfocar_dos_veces_no_repite_la_busqueda_inicial(monkeypatch):
    campo, _texto_estado, _resultados, llamadas = _construir(
        monkeypatch, ApiExito(datos=["Ana"])
    )

    await campo.on_focus(None)
    await campo.on_focus(None)

    assert llamadas == [""]


async def test_escribir_menos_de_tres_caracteres_igual_busca(monkeypatch):
    campo, _texto_estado, resultados, llamadas = _construir(
        monkeypatch, ApiExito(datos=["Ana"])
    )

    campo.value = "an"
    await campo.on_change(None)

    assert llamadas == ["an"]
    assert resultados.visible is True
