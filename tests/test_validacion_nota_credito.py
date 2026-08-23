import validacion_nota_credito as v
from estado_nota_credito import EstadoNotaCredito, LineaNcSeleccionable


def _linea(**overrides) -> LineaNcSeleccionable:
    base = dict(
        linea_factura_origen_id="l-1",
        numero_linea=1,
        codigo_cabys_aplicado="8399000000000",
        unidad_medida_comercial="Unid",
        cantidad_origen=10,
        precio_unitario=100,
        subtotal_origen=1000,
        porcentaje_impuesto_aplicado=13,
        seleccionada=False,
        cantidad_acreditar=10,
    )
    base.update(overrides)
    return LineaNcSeleccionable(**base)


def _estado(**overrides) -> EstadoNotaCredito:
    base = dict(
        factura_origen_id="f-1",
        factura_origen_consecutivo="00100001010000000001",
        cliente_nombre="Ana",
        lineas=[_linea()],
        moneda="CRC",
    )
    base.update(overrides)
    return EstadoNotaCredito(**base)


def test_validar_paso1_requiere_codigo_referencia():
    estado = _estado()
    errores = v.validar_paso1(estado)
    assert "codigo_referencia" in errores


def test_validar_paso1_valido_con_codigo_referencia():
    estado = _estado()
    estado.codigo_referencia = "06"
    assert v.validar_paso1(estado) == {}


def test_validar_paso1_codigo_99_requiere_otro():
    estado = _estado()
    estado.codigo_referencia = "99"
    errores = v.validar_paso1(estado)
    assert "codigo_referencia_otro" in errores


def test_validar_paso1_razon_excede_180_caracteres():
    estado = _estado()
    estado.codigo_referencia = "06"
    estado.razon = "x" * 181
    errores = v.validar_paso1(estado)
    assert "razon" in errores


def test_validar_paso2_requiere_al_menos_una_linea_seleccionada():
    estado = _estado(lineas=[_linea(seleccionada=False)])
    errores = v.validar_paso2(estado)
    assert "lineas" in errores


def test_validar_paso2_valido_con_una_linea_seleccionada_dentro_de_rango():
    estado = _estado(
        lineas=[_linea(seleccionada=True, cantidad_origen=10, cantidad_acreditar=5)]
    )
    assert v.validar_paso2(estado) == {}


def test_validar_paso2_cantidad_acreditar_debe_ser_mayor_a_cero():
    estado = _estado(
        lineas=[_linea(seleccionada=True, cantidad_origen=10, cantidad_acreditar=0)]
    )
    errores = v.validar_paso2(estado)
    assert "lineas.0.cantidad_acreditar" in errores


def test_validar_paso2_cantidad_acreditar_negativa_es_invalida():
    estado = _estado(
        lineas=[_linea(seleccionada=True, cantidad_origen=10, cantidad_acreditar=-1)]
    )
    errores = v.validar_paso2(estado)
    assert "lineas.0.cantidad_acreditar" in errores


def test_validar_paso2_cantidad_acreditar_no_puede_exceder_cantidad_origen():
    estado = _estado(
        lineas=[_linea(seleccionada=True, cantidad_origen=10, cantidad_acreditar=10.5)]
    )
    errores = v.validar_paso2(estado)
    assert "lineas.0.cantidad_acreditar" in errores


def test_validar_paso2_cantidad_acreditar_igual_a_cantidad_origen_es_valida():
    estado = _estado(
        lineas=[_linea(seleccionada=True, cantidad_origen=10, cantidad_acreditar=10)]
    )
    assert v.validar_paso2(estado) == {}


def test_validar_paso2_ignora_lineas_no_seleccionadas():
    lineas = [
        _linea(linea_factura_origen_id="l-1", seleccionada=True, cantidad_origen=10, cantidad_acreditar=5),
        _linea(linea_factura_origen_id="l-2", seleccionada=False, cantidad_origen=10, cantidad_acreditar=999),
    ]
    estado = _estado(lineas=lineas)
    assert v.validar_paso2(estado) == {}


def test_validar_paso2_no_valida_tope_de_monto():
    estado = _estado(
        lineas=[
            _linea(
                seleccionada=True,
                cantidad_origen=1000,
                cantidad_acreditar=1000,
                subtotal_origen=1_000_000_000,
            )
        ]
    )
    assert v.validar_paso2(estado) == {}
