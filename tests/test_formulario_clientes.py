from api.cliente import ApiExito
from api.clientes import Cliente, ClienteCreado, DatosCliente
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
        "numero_identificacion": columna.controls[2],
        "provincia": columna.controls[5].controls[0],
        "canton": columna.controls[5].controls[1],
        "distrito": columna.controls[5].controls[2],
        "otras_senas": columna.controls[5].controls[3],
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

    assert campos["canton"].error
    assert campos["distrito"].error
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
