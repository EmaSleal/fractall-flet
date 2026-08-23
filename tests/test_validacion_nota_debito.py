import validacion_nota_debito as v
from estado_factura import LineaWizard
from estado_nota_debito import EstadoNotaDebito


def _estado(**overrides) -> EstadoNotaDebito:
    base = dict(
        factura_origen_id="f-1",
        factura_origen_consecutivo="00100001010000000001",
        cliente_nombre="Ana",
        moneda="CRC",
    )
    base.update(overrides)
    return EstadoNotaDebito(**base)


def test_validar_paso1_requiere_codigo_referencia():
    estado = _estado()
    errores = v.validar_paso1(estado)
    assert "codigo_referencia" in errores


def test_validar_paso1_valido_con_codigo_referencia():
    estado = _estado()
    estado.codigo_referencia = "01"
    estado.razon = "Ajuste de precio"
    assert v.validar_paso1(estado) == {}


def test_validar_paso1_razon_vacia_es_invalida():
    estado = _estado()
    estado.codigo_referencia = "01"
    errores = v.validar_paso1(estado)
    assert "razon" in errores


def test_validar_paso1_razon_solo_espacios_es_invalida():
    estado = _estado()
    estado.codigo_referencia = "01"
    estado.razon = "   "
    errores = v.validar_paso1(estado)
    assert "razon" in errores


def test_validar_paso1_codigo_99_requiere_otro():
    estado = _estado()
    estado.codigo_referencia = "99"
    errores = v.validar_paso1(estado)
    assert "codigo_referencia_otro" in errores


def test_validar_paso1_codigo_99_con_otro_es_valido():
    estado = _estado()
    estado.codigo_referencia = "99"
    estado.codigo_referencia_otro = "Ajuste manual"
    estado.razon = "Ajuste de precio"
    assert v.validar_paso1(estado) == {}


def test_validar_paso1_codigo_99_con_otro_solo_espacios_es_invalido():
    estado = _estado()
    estado.codigo_referencia = "99"
    estado.codigo_referencia_otro = "   "
    errores = v.validar_paso1(estado)
    assert "codigo_referencia_otro" in errores


def test_validar_paso1_codigo_distinto_de_99_no_requiere_otro():
    estado = _estado()
    estado.codigo_referencia = "01"
    estado.codigo_referencia_otro = ""
    estado.razon = "Ajuste de precio"
    assert v.validar_paso1(estado) == {}


def test_validar_paso1_razon_dentro_del_limite_es_valida():
    estado = _estado()
    estado.codigo_referencia = "01"
    estado.razon = "x" * 180
    assert v.validar_paso1(estado) == {}


def test_validar_paso1_razon_excede_180_caracteres():
    estado = _estado()
    estado.codigo_referencia = "01"
    estado.razon = "x" * 181
    errores = v.validar_paso1(estado)
    assert "razon" in errores


def test_validar_paso2_reusa_validacion_de_factura():
    estado = _estado()
    estado.lineas = [LineaWizard(producto_id=None, cantidad=0, precio_unitario=-1)]
    errores = v.validar_paso2(estado)
    assert "lineas.0.producto_id" in errores
    assert "lineas.0.cantidad" in errores
    assert "lineas.0.precio_unitario" in errores


def test_validar_paso2_valido():
    estado = _estado()
    estado.lineas = [LineaWizard(producto_id="p-1", cantidad=1, precio_unitario=100)]
    assert v.validar_paso2(estado) == {}
