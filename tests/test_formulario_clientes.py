from api.cliente import ApiExito, ApiFallo
from api.clientes import ActividadHacienda, Cliente, ClienteCreado, ConsultaHacienda, DatosCliente
from api.errores import ErrorApi
import ui.paginas.clientes.formulario as formulario_module
from ui.paginas.clientes.formulario import construir_formulario_cliente


class PageFalsa:
    width = 1200

    def navigate(self, ruta, **kw):
        pass

    def update(self):
        pass

    def run_task(self, handler, *a, **kw):
        pass


def _construir(cliente_inicial=None):
    llamadas = {"guardar": [], "exito": []}

    async def guardar(datos: DatosCliente):
        llamadas["guardar"].append(datos)
        return ApiExito(datos=ClienteCreado(id="c-nuevo"))

    def al_exito(datos):
        llamadas["exito"].append(datos)

    columna = construir_formulario_cliente(
        PageFalsa(), cliente_inicial, guardar, al_exito
    )
    campos = {
        "nombre": columna.controls[0],
        "tipo_identificacion": columna.controls[1],
        # controls[2] es un ft.Row([campo_numero_identificacion, boton_buscar_hacienda])
        # desde que se agregó el botón "Buscar en Hacienda" -- ver formulario.py.
        "numero_identificacion": columna.controls[2].controls[0],
        "boton_hacienda": columna.controls[2].controls[1],
        "codigo_actividad": columna.controls[5],
        "codigo_actividad_dropdown": columna.controls[6],
        "provincia": columna.controls[8].controls[0],
        "canton": columna.controls[8].controls[1],
        "distrito": columna.controls[8].controls[2],
        "otras_senas": columna.controls[8].controls[3],
    }
    boton_guardar = columna.controls[-1]
    return campos, boton_guardar, llamadas


async def test_formulario_rechaza_nombre_vacio():
    campos, boton, llamadas = _construir()
    campos["tipo_identificacion"].value = "01"
    campos["numero_identificacion"].value = "123"

    await boton.on_click(None)

    assert campos["nombre"].error == "Requerido"
    assert llamadas["guardar"] == []


async def test_formulario_rechaza_tipo_identificacion_vacio():
    campos, boton, llamadas = _construir()
    campos["nombre"].value = "Ana"
    campos["numero_identificacion"].value = "123"

    await boton.on_click(None)

    assert campos["tipo_identificacion"].error_text == "Seleccioná un tipo"
    assert llamadas["guardar"] == []


async def test_formulario_bloque_ubicacion_parcial_falla():
    campos, boton, llamadas = _construir()
    campos["nombre"].value = "Ana"
    campos["tipo_identificacion"].value = "01"
    campos["numero_identificacion"].value = "123"
    campos["provincia"].value = "1"

    await boton.on_click(None)

    assert campos["canton"].error_text
    assert campos["distrito"].error_text
    assert campos["otras_senas"].error
    assert llamadas["guardar"] == []


async def test_formulario_valido_llama_guardar_y_al_exito():
    campos, boton, llamadas = _construir()
    campos["nombre"].value = "Ana"
    campos["tipo_identificacion"].value = "01"
    campos["numero_identificacion"].value = "123"

    await boton.on_click(None)

    assert len(llamadas["guardar"]) == 1
    assert llamadas["guardar"][0].nombre == "Ana"
    assert len(llamadas["exito"]) == 1
    assert llamadas["exito"][0].id == "c-nuevo"


async def test_formulario_precarga_valores_de_cliente_existente():
    cliente = Cliente(
        id="c-1",
        nombre="Ana",
        tipo_identificacion="02",
        numero_identificacion="456",
        codigo_actividad=None,
        codigo_provincia=None,
        canton=None,
        distrito=None,
        otras_senas=None,
        telefono=None,
        email=None,
        requiere_factura_electronica=False,
    )
    campos, _boton, _llamadas = _construir(cliente)

    assert campos["nombre"].value == "Ana"
    assert campos["tipo_identificacion"].value == "02"
    assert campos["numero_identificacion"].value == "456"


def _mockear_consultar_hacienda(monkeypatch, resultado):
    async def _fake(identificacion):
        return resultado

    monkeypatch.setattr(formulario_module, "consultar_hacienda", _fake)


async def test_boton_buscar_hacienda_completa_nombre_y_tipo(monkeypatch):
    _mockear_consultar_hacienda(
        monkeypatch,
        ApiExito(
            datos=ConsultaHacienda(
                exitosa=True,
                nombre="Persona Consultada S.A.",
                tipo_identificacion="02",
                actividades=[],
                mensaje_error=None,
            )
        ),
    )
    campos, _boton, _llamadas = _construir()
    campos["numero_identificacion"].value = "310987654"

    await campos["boton_hacienda"].on_click(None)

    assert campos["nombre"].value == "Persona Consultada S.A."
    assert campos["tipo_identificacion"].value == "02"


async def test_boton_buscar_hacienda_no_encontrado_no_pisa_nombre(monkeypatch):
    _mockear_consultar_hacienda(
        monkeypatch,
        ApiExito(
            datos=ConsultaHacienda(
                exitosa=False,
                nombre=None,
                tipo_identificacion=None,
                actividades=[],
                mensaje_error="No encontrada en Hacienda",
            )
        ),
    )
    campos, _boton, _llamadas = _construir()
    campos["nombre"].value = "Nombre tipeado a mano"
    campos["numero_identificacion"].value = "999999999"

    await campos["boton_hacienda"].on_click(None)

    assert campos["nombre"].value == "Nombre tipeado a mano"


async def test_boton_buscar_hacienda_con_actividades_activas_muestra_dropdown(monkeypatch):
    _mockear_consultar_hacienda(
        monkeypatch,
        ApiExito(
            datos=ConsultaHacienda(
                exitosa=True,
                nombre="Persona Consultada S.A.",
                tipo_identificacion="02",
                actividades=[
                    ActividadHacienda(codigo="469100", descripcion="Secundaria", tipo="S", estado="A"),
                    ActividadHacienda(codigo="620100", descripcion="Principal", tipo="P", estado="A"),
                    ActividadHacienda(codigo="111100", descripcion="Inactiva", tipo="S", estado="I"),
                ],
                mensaje_error=None,
            )
        ),
    )
    campos, _boton, _llamadas = _construir()
    campos["numero_identificacion"].value = "310987654"

    await campos["boton_hacienda"].on_click(None)

    # La inactiva (estado="I") queda afuera; se autoselecciona la de tipo="P".
    assert len(campos["codigo_actividad_dropdown"].options) == 2
    assert campos["codigo_actividad_dropdown"].value == "620100"
    assert campos["codigo_actividad"].value == "620100"
    assert campos["codigo_actividad_dropdown"].visible is True
    assert campos["codigo_actividad"].visible is False


async def test_al_cambiar_actividad_en_dropdown_actualiza_campo_oculto(monkeypatch):
    _mockear_consultar_hacienda(
        monkeypatch,
        ApiExito(
            datos=ConsultaHacienda(
                exitosa=True,
                nombre="Persona Consultada S.A.",
                tipo_identificacion="02",
                actividades=[
                    ActividadHacienda(codigo="469100", descripcion="Secundaria", tipo="S", estado="A"),
                    ActividadHacienda(codigo="620100", descripcion="Principal", tipo="P", estado="A"),
                ],
                mensaje_error=None,
            )
        ),
    )
    campos, _boton, _llamadas = _construir()
    campos["numero_identificacion"].value = "310987654"
    await campos["boton_hacienda"].on_click(None)

    campos["codigo_actividad_dropdown"].value = "469100"

    class EventoFalso:
        control = campos["codigo_actividad_dropdown"]

    campos["codigo_actividad_dropdown"].on_select(EventoFalso())

    assert campos["codigo_actividad"].value == "469100"


async def test_auto_busqueda_dispara_al_llegar_a_la_longitud_del_tipo(monkeypatch):
    llamadas = []

    async def _fake(identificacion):
        llamadas.append(identificacion)
        return ApiExito(
            datos=ConsultaHacienda(
                exitosa=True,
                nombre="Auto Encontrado S.A.",
                tipo_identificacion="02",
                actividades=[],
                mensaje_error=None,
            )
        )

    monkeypatch.setattr(formulario_module, "consultar_hacienda", _fake)
    campos, _boton, _llamadas = _construir()
    campos["tipo_identificacion"].value = "02"  # Jurídica -- 10 caracteres

    campos["numero_identificacion"].value = "310987654"  # 9 -- todavía no dispara
    await campos["numero_identificacion"].on_change(None)
    assert llamadas == []

    campos["numero_identificacion"].value = "3109876540"  # 10 -- dispara
    await campos["numero_identificacion"].on_change(None)
    assert llamadas == ["3109876540"]

    # Sin cambio de valor: no se reintenta la misma búsqueda.
    await campos["numero_identificacion"].on_change(None)
    assert llamadas == ["3109876540"]


async def test_auto_busqueda_no_exige_solo_digitos(monkeypatch):
    """Cantidad de caracteres por tipo sigue activa; el filtro de solo-dígitos
    quedó desactivado a propósito (ver catalogos.LONGITUDES_IDENTIFICACION)."""
    llamadas = []

    async def _fake(identificacion):
        llamadas.append(identificacion)
        return ApiExito(
            datos=ConsultaHacienda(
                exitosa=False,
                nombre=None,
                tipo_identificacion=None,
                actividades=[],
                mensaje_error="No encontrada",
            )
        )

    monkeypatch.setattr(formulario_module, "consultar_hacienda", _fake)
    campos, _boton, _llamadas = _construir()
    campos["tipo_identificacion"].value = "02"  # Jurídica -- 10 caracteres

    campos["numero_identificacion"].value = "31098A654B"  # 10 caracteres, con letras
    await campos["numero_identificacion"].on_change(None)

    assert llamadas == ["31098A654B"]


async def test_boton_buscar_hacienda_error_de_red_muestra_mensaje_generico(monkeypatch):
    _mockear_consultar_hacienda(
        monkeypatch, ApiFallo(error=ErrorApi(mensaje="Timeout", status=504))
    )
    campos, _boton, _llamadas = _construir()
    campos["numero_identificacion"].value = "310987654"

    await campos["boton_hacienda"].on_click(None)

    # No debe reventar ni pisar nombre -- solo informar el error (mostrar_estado_hacienda).
    assert campos["nombre"].value == ""
