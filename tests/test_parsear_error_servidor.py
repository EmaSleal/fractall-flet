from parsear_error_servidor import parsear_error_servidor


def test_404_va_a_paso1():
    error = parsear_error_servidor(404, "irrelevante")
    assert error.paso == 1
    assert error.campo is None


def test_503_va_a_paso1():
    error = parsear_error_servidor(503, "irrelevante")
    assert error.paso == 1


def test_400_cliente():
    error = parsear_error_servidor(400, "clienteId: no existe")
    assert error.paso == 1
    assert error.campo == "cliente_id"


def test_400_plazo_credito():
    error = parsear_error_servidor(400, "plazoCredito: es requerido para condición 02")
    assert error.paso == 1
    assert error.campo == "plazo_credito"


def test_400_tipo_cambio():
    error = parsear_error_servidor(400, "tipoCambio: fuera de rango")
    assert error.paso == 1
    assert error.campo == "tipo_cambio"


def test_400_lineas_va_a_paso2():
    error = parsear_error_servidor(400, "lineas[0].productoId: no existe")
    assert error.paso == 2
    assert error.campo is None


def test_400_medios_pago_va_a_paso3():
    error = parsear_error_servidor(400, "mediosPago: no coincide con el total")
    assert error.paso == 3
    assert error.campo is None


def test_400_desconocido_cae_a_paso1():
    error = parsear_error_servidor(400, "algo totalmente inesperado")
    assert error.paso == 1
    assert error.campo is None


def test_orden_de_prioridad_cliente_antes_que_condicion_venta():
    # el mensaje contiene ambas substrings; "cliente" gana por ir primero
    error = parsear_error_servidor(400, "clienteId y condicionVenta inválidos")
    assert error.campo == "cliente_id"
