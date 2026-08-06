import api.productos as productos_module
from api.cliente import ApiExito, ApiFallo
from api.errores import ErrorApi
from api.productos import (
    DatosProducto,
    PaginaProductos,
    Producto,
    ProductoCreado,
    actualizar_producto,
    alternar_activo,
    buscar_productos,
    crear_producto,
    listar_productos,
    obtener_producto,
)


def _mockear_peticion_autenticada(monkeypatch, resultado, capturar_en=None):
    async def _fake(*args, **kwargs):
        if capturar_en is not None:
            capturar_en.append(kwargs)
        return resultado

    monkeypatch.setattr(productos_module, "peticion_autenticada", _fake)


async def test_listar_productos_manda_activo_explicito(monkeypatch):
    llamadas = []
    _mockear_peticion_autenticada(
        monkeypatch, ApiExito(datos={"items": [], "nextCursor": None}), capturar_en=llamadas
    )

    await listar_productos()

    assert llamadas[0]["parametros"]["activo"] is True

    await listar_productos(activo=False)
    assert llamadas[1]["parametros"]["activo"] is False


async def test_listar_productos_mapea_items(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(
            datos={
                "items": [
                    {
                        "id": "p-1",
                        "codigo": "PROD-1",
                        "descripcion": "Producto 1",
                        "precioVenta": 1000,
                        "activo": True,
                    }
                ],
                "nextCursor": "p-1",
            }
        ),
    )

    resultado = await listar_productos()

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, PaginaProductos)
    assert isinstance(resultado.datos.items[0], Producto)
    assert resultado.datos.next_cursor == "p-1"


async def test_obtener_producto_404_devuelve_none(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch, ApiFallo(error=ErrorApi(mensaje="No encontrado.", status=404))
    )

    resultado = await obtener_producto("p-x")

    assert isinstance(resultado, ApiExito)
    assert resultado.datos is None


async def test_crear_producto(monkeypatch):
    llamadas = []
    _mockear_peticion_autenticada(
        monkeypatch, ApiExito(datos={"id": "p-nuevo"}), capturar_en=llamadas
    )

    resultado = await crear_producto(
        DatosProducto(
            codigo="PROD-1",
            descripcion="Producto 1",
            codigo_cabys="1234567890123",
            precio_venta=1000,
        )
    )

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, ProductoCreado)
    assert resultado.datos.id == "p-nuevo"
    assert llamadas[0]["cuerpo"]["codigoCabys"] == "1234567890123"


async def test_actualizar_producto(monkeypatch):
    _mockear_peticion_autenticada(monkeypatch, ApiExito(datos={}))

    resultado = await actualizar_producto(
        "p-1",
        DatosProducto(
            codigo="PROD-1", descripcion="X", codigo_cabys="123", precio_venta=1
        ),
    )

    assert isinstance(resultado, ApiExito)


async def test_alternar_activo_manda_solo_ese_campo(monkeypatch):
    llamadas = []
    _mockear_peticion_autenticada(monkeypatch, ApiExito(datos={}), capturar_en=llamadas)

    resultado = await alternar_activo("p-1", False)

    assert isinstance(resultado, ApiExito)
    assert llamadas[0]["cuerpo"] == {"activo": False}


async def test_buscar_productos_fuerza_activo_true(monkeypatch):
    llamadas = []
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(datos={"items": [{"id": "p-1", "codigo": "X"}], "nextCursor": None}),
        capturar_en=llamadas,
    )

    resultado = await buscar_productos("arroz")

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos[0], Producto)
    assert llamadas[0]["parametros"]["activo"] is True
    assert llamadas[0]["parametros"]["q"] == "arroz"
