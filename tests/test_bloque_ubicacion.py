import ui.componentes.bloque_ubicacion as bloque_module
from api.cliente import ApiExito
from api.ubicacion import Canton, Distrito, Provincia
from ui.componentes.bloque_ubicacion import construir_bloque_ubicacion


class PageFalsa:
    def update(self):
        pass

    def run_task(self, handler, *a, **kw):
        pass


def _mockear_listados(monkeypatch, *, provincias=None, cantones=None, distritos=None):
    async def _provincias(*a, **kw):
        return ApiExito(datos=provincias or [])

    async def _cantones(*a, **kw):
        return ApiExito(datos=cantones or [])

    async def _distritos(*a, **kw):
        return ApiExito(datos=distritos or [])

    monkeypatch.setattr(bloque_module, "listar_provincias", _provincias)
    monkeypatch.setattr(bloque_module, "listar_cantones", _cantones)
    monkeypatch.setattr(bloque_module, "listar_distritos", _distritos)


async def test_cargar_provincias_puebla_opciones(monkeypatch):
    _mockear_listados(monkeypatch, provincias=[Provincia(codigo="1", nombre="San José")])
    bloque = construir_bloque_ubicacion(PageFalsa())

    await bloque.cargar_provincias()

    assert [o.key for o in bloque.provincia.options] == ["1"]


async def test_elegir_provincia_habilita_y_puebla_canton(monkeypatch):
    _mockear_listados(
        monkeypatch, cantones=[Canton(provincia_codigo="1", codigo="01", nombre="San José")]
    )
    bloque = construir_bloque_ubicacion(PageFalsa())
    bloque.provincia.value = "1"

    await bloque.provincia.on_select(None)

    assert bloque.canton.disabled is False
    assert [o.key for o in bloque.canton.options] == ["01"]


async def test_elegir_provincia_resetea_canton_y_distrito(monkeypatch):
    _mockear_listados(monkeypatch)
    bloque = construir_bloque_ubicacion(PageFalsa())
    bloque.canton.value = "01"
    bloque.distrito.value = "01"
    bloque.provincia.value = "2"

    await bloque.provincia.on_select(None)

    assert bloque.canton.value is None
    assert bloque.distrito.value is None
    assert bloque.distrito.disabled is True


async def test_elegir_canton_habilita_y_puebla_distrito(monkeypatch):
    _mockear_listados(
        monkeypatch,
        distritos=[Distrito(provincia_codigo="1", canton_codigo="01", codigo="01", nombre="Carmen")],
    )
    bloque = construir_bloque_ubicacion(PageFalsa())
    bloque.provincia.value = "1"
    bloque.canton.value = "01"

    await bloque.canton.on_select(None)

    assert bloque.distrito.disabled is False
    assert [o.key for o in bloque.distrito.options] == ["01"]


async def test_sincronizar_cascada_reconstruye_opciones_para_edicion(monkeypatch):
    _mockear_listados(
        monkeypatch,
        cantones=[Canton(provincia_codigo="1", codigo="01", nombre="San José")],
        distritos=[Distrito(provincia_codigo="1", canton_codigo="01", codigo="01", nombre="Carmen")],
    )
    bloque = construir_bloque_ubicacion(PageFalsa())
    bloque.provincia.value = "1"
    bloque.canton.value = "01"
    bloque.distrito.value = "01"

    await bloque.sincronizar_cascada()

    assert bloque.canton.disabled is False
    assert bloque.distrito.disabled is False
    assert bloque.canton.value == "01"
    assert bloque.distrito.value == "01"
