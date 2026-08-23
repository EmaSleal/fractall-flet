from parsear_error_servidor_tiquete import parsear_error_servidor_tiquete


def test_404_va_a_paso1():
    error = parsear_error_servidor_tiquete(404, "irrelevante")
    assert error.paso == 1
    assert error.campo is None


def test_503_va_a_paso1():
    error = parsear_error_servidor_tiquete(503, "irrelevante")
    assert error.paso == 1


def test_400_cliente():
    error = parsear_error_servidor_tiquete(400, "clienteId: no existe")
    assert error.paso == 1
    assert error.campo == "cliente_id"


def test_400_plazo_credito():
    error = parsear_error_servidor_tiquete(400, "plazoCredito: es requerido para condición 02")
    assert error.paso == 1
    assert error.campo == "plazo_credito"


def test_400_medio_pago_va_a_paso1():
    error = parsear_error_servidor_tiquete(400, "medioPago: valor inválido")
    assert error.paso == 1
    assert error.campo == "medio_pago"


def test_400_tipo_cambio():
    error = parsear_error_servidor_tiquete(400, "tipoCambio: fuera de rango")
    assert error.paso == 1
    assert error.campo == "tipo_cambio"


def test_400_lineas_va_a_paso2():
    error = parsear_error_servidor_tiquete(400, "lineas[0].productoId: no existe")
    assert error.paso == 2
    assert error.campo is None


def test_400_desconocido_cae_a_paso1():
    error = parsear_error_servidor_tiquete(400, "algo totalmente inesperado")
    assert error.paso == 1
    assert error.campo is None


def test_orden_de_prioridad_cliente_antes_que_condicion_venta():
    error = parsear_error_servidor_tiquete(400, "clienteId y condicionVenta inválidos")
    assert error.campo == "cliente_id"
