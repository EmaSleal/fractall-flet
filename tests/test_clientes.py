import api.clientes as clientes_module
from api.cliente import ApiExito, ApiFallo
from api.clientes import (
    Cliente,
    ClienteCreado,
    ClienteExoneracion,
    DatosCliente,
    DatosExoneracion,
    PaginaClientes,
    actualizar_cliente,
    buscar_clientes,
    crear_cliente,
    crear_exoneracion,
    desactivar_exoneracion,
    listar_clientes,
    listar_exoneraciones,
    obtener_cliente,
)
from api.errores import ErrorApi


def _mockear_peticion_autenticada(monkeypatch, resultado, capturar_en=None):
    async def _fake(*args, **kwargs):
        if capturar_en is not None:
            capturar_en.append(kwargs)
        return resultado

    monkeypatch.setattr(clientes_module, "peticion_autenticada", _fake)


async def test_listar_clientes(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(
            datos={
                "items": [
                    {
                        "id": "c-1",
                        "nombre": "Ana",
                        "tipoIdentificacion": "01",
                        "numeroIdentificacion": "123",
                        "requiereFacturaElectronica": True,
                    }
                ],
                "nextCursor": "c-1",
            }
        ),
    )

    resultado = await listar_clientes(q="ana")

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, PaginaClientes)
    assert len(resultado.datos.items) == 1
    assert isinstance(resultado.datos.items[0], Cliente)
    assert resultado.datos.next_cursor == "c-1"


async def test_listar_clientes_pasa_parametros_correctos(monkeypatch):
    llamadas = []
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(datos={"items": [], "nextCursor": None}),
        capturar_en=llamadas,
    )

    await listar_clientes(q="ana", cursor="cur-1", limit=10)

    assert llamadas[0]["parametros"] == {"limit": 10, "q": "ana", "cursor": "cur-1"}


async def test_obtener_cliente_404_devuelve_none(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiFallo(error=ErrorApi(mensaje="No encontrado.", status=404)),
    )

    resultado = await obtener_cliente("c-inexistente")

    assert isinstance(resultado, ApiExito)
    assert resultado.datos is None


async def test_obtener_cliente_otro_error_se_propaga(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiFallo(error=ErrorApi(mensaje="No autenticado.", status=401)),
    )

    resultado = await obtener_cliente("c-1")

    assert isinstance(resultado, ApiFallo)


async def test_crear_cliente_convierte_vacios_a_null(monkeypatch):
    llamadas = []
    _mockear_peticion_autenticada(
        monkeypatch, ApiExito(datos={"id": "c-nuevo"}), capturar_en=llamadas
    )

    datos = DatosCliente(
        nombre="Ana",
        tipo_identificacion="01",
        numero_identificacion="123",
        email="  ",
        telefono="",
    )
    resultado = await crear_cliente(datos)

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, ClienteCreado)
    assert resultado.datos.id == "c-nuevo"
    cuerpo = llamadas[0]["cuerpo"]
    assert cuerpo["email"] is None
    assert cuerpo["telefono"] is None
    assert cuerpo["nombre"] == "Ana"


async def test_actualizar_cliente(monkeypatch):
    _mockear_peticion_autenticada(monkeypatch, ApiExito(datos={}))

    resultado = await actualizar_cliente(
        "c-1", DatosCliente(nombre="Ana", tipo_identificacion="01", numero_identificacion="1")
    )

    assert isinstance(resultado, ApiExito)


async def test_listar_exoneraciones(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(
            datos=[
                {
                    "id": "e-1",
                    "clienteId": "c-1",
                    "tipoDocumento": "01",
                    "fechaEmision": "2026-01-01T00:00:00Z",
                    "porcentajeExoneracion": 100,
                    "activo": True,
                    "vigente": True,
                }
            ]
        ),
    )

    resultado = await listar_exoneraciones("c-1")

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos[0], ClienteExoneracion)
    assert resultado.datos[0].activo is True


async def test_crear_exoneracion(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(
            datos={
                "id": "e-1",
                "clienteId": "c-1",
                "tipoDocumento": "99",
                "fechaEmision": "2026-01-01T00:00:00Z",
                "porcentajeExoneracion": 50,
                "activo": True,
                "vigente": True,
            }
        ),
    )

    resultado = await crear_exoneracion(
        "c-1",
        DatosExoneracion(
            tipo_documento="99",
            numero_documento="123",
            nombre_institucion="Institución",
            fecha_emision="2026-01-01",
            porcentaje_exoneracion=50,
        ),
    )

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, ClienteExoneracion)


async def test_desactivar_exoneracion(monkeypatch):
    _mockear_peticion_autenticada(monkeypatch, ApiExito(datos={}))

    resultado = await desactivar_exoneracion("e-1")

    assert isinstance(resultado, ApiExito)


async def test_buscar_clientes_devuelve_lista_plana(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(datos={"items": [{"id": "c-1", "nombre": "Ana"}], "nextCursor": "c-1"}),
    )

    resultado = await buscar_clientes("ana")

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, list)
    assert isinstance(resultado.datos[0], Cliente)
