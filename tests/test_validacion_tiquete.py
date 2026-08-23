import validacion_tiquete as v
from estado_tiquete import EstadoTiquete
from estado_factura import LineaWizard


def test_validar_paso1_sin_cliente_es_valido():
    estado = EstadoTiquete()
    assert "cliente_id" not in v.validar_paso1(estado)
    assert v.validar_paso1(estado) == {}


def test_validar_paso1_con_cliente_tambien_es_valido():
    estado = EstadoTiquete()
    estado.establecer_cliente("c-1", "Ana", "01 123")
    assert v.validar_paso1(estado) == {}


def test_validar_paso1_credito_requiere_plazo():
    estado = EstadoTiquete()
    estado.establecer_condicion_venta("02")
    errores = v.validar_paso1(estado)
    assert "plazo_credito" in errores


def test_validar_paso1_otros_requiere_detalle():
    estado = EstadoTiquete()
    estado.establecer_condicion_venta("99")
    errores = v.validar_paso1(estado)
    assert "condicion_venta_otros" in errores


def test_validar_paso1_usd_fuera_de_rango():
    estado = EstadoTiquete()
    estado.establecer_moneda("USD")
    estado.tipo_cambio = 100.0
    errores = v.validar_paso1(estado)
    assert "tipo_cambio" in errores


def test_validar_paso1_usd_en_rango_es_valido():
    estado = EstadoTiquete()
    estado.establecer_moneda("USD")
    estado.tipo_cambio = 550.0
    assert v.validar_paso1(estado) == {}


def test_validar_paso1_moneda_distinta_de_crc_usd_requiere_tipo_cambio():
    estado = EstadoTiquete()
    estado.moneda = "EUR"
    estado.tipo_cambio = 0.0
    errores = v.validar_paso1(estado)
    assert "tipo_cambio" in errores


def test_validar_paso1_moneda_distinta_de_crc_usd_con_tipo_cambio_es_valido():
    estado = EstadoTiquete()
    estado.moneda = "EUR"
    estado.tipo_cambio = 620.5
    assert v.validar_paso1(estado) == {}


def test_validar_paso2_reusa_validacion_de_factura():
    estado = EstadoTiquete()
    estado.lineas = [LineaWizard(producto_id=None, cantidad=0, precio_unitario=-1)]
    errores = v.validar_paso2(estado)
    assert "lineas.0.producto_id" in errores
    assert "lineas.0.cantidad" in errores
    assert "lineas.0.precio_unitario" in errores


def test_validar_paso2_valido():
    estado = EstadoTiquete()
    estado.lineas = [LineaWizard(producto_id="p-1", cantidad=1, precio_unitario=100)]
    assert v.validar_paso2(estado) == {}
