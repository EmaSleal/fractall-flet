from api.cliente import ApiExito
from api.productos import DatosProducto, Producto, ProductoCreado
from ui.paginas.productos.formulario import construir_formulario_producto


class PageFalsa:
    width = 1200

    def navigate(self, ruta, **kw):
        pass

    def update(self):
        pass

    def run_task(self, handler, *a, **kw):
        pass


def _producto_existente(**overrides) -> Producto:
    base = dict(
        id="p-1",
        codigo="PROD-1",
        descripcion="Producto 1",
        codigo_cabys="1234567890123",
        descripcion_cabys="Arroz",
        cabys_validado_en=None,
        codigo_unidad_fe=None,
        precio_venta=1000,
        gravado=True,
        porcentaje_impuesto=13,
        activo=True,
    )
    base.update(overrides)
    return Producto(**base)


def _construir(producto_inicial=None, unidades=None):
    llamadas = {"guardar": [], "exito": []}

    async def guardar(datos: DatosProducto):
        llamadas["guardar"].append(datos)
        return ApiExito(datos=ProductoCreado(id="p-nuevo"))

    def al_exito(datos):
        llamadas["exito"].append(datos)

    columna = construir_formulario_producto(
        PageFalsa(), producto_inicial, unidades or [], guardar, al_exito
    )
    campos = {
        "codigo": columna.controls[0],
        "descripcion": columna.controls[1],
        "precio": columna.controls[4],
    }
    boton_guardar = columna.controls[-1]
    texto_error = columna.controls[-2]
    return campos, boton_guardar, texto_error, llamadas


async def test_formulario_rechaza_codigo_vacio():
    campos, boton, _texto_error, llamadas = _construir()
    campos["descripcion"].value = "Producto"
    campos["precio"].value = "100"

    await boton.on_click(None)

    assert campos["codigo"].error == "Requerido"
    assert llamadas["guardar"] == []


async def test_formulario_rechaza_sin_cabys_elegido():
    campos, boton, texto_error, llamadas = _construir()
    campos["codigo"].value = "PROD-1"
    campos["descripcion"].value = "Producto"
    campos["precio"].value = "100"

    await boton.on_click(None)

    assert texto_error.visible is True
    assert llamadas["guardar"] == []


async def test_formulario_rechaza_precio_invalido():
    producto = _producto_existente()
    campos, boton, _texto_error, llamadas = _construir(producto)
    campos["precio"].value = "no-es-un-numero"

    await boton.on_click(None)

    assert campos["precio"].error
    assert llamadas["guardar"] == []


async def test_formulario_valido_llama_guardar_con_cabys_precargado():
    producto = _producto_existente()
    campos, boton, _texto_error, llamadas = _construir(producto)

    await boton.on_click(None)

    assert len(llamadas["guardar"]) == 1
    datos = llamadas["guardar"][0]
    assert datos.codigo_cabys == "1234567890123"
    assert len(llamadas["exito"]) == 1
