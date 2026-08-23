from parsear_error_servidor_nota_debito import parsear_error_servidor_nota_debito


def test_409_va_a_paso1_sin_interpretar_el_mensaje():
    error = parsear_error_servidor_nota_debito(409, "La factura origen no está ACEPTADO")
    assert error.paso == 1
    assert error.campo is None
    assert error.mensaje == "La factura origen no está ACEPTADO"


def test_404_va_a_paso1():
    error = parsear_error_servidor_nota_debito(404, "irrelevante")
    assert error.paso == 1
    assert error.campo is None


def test_400_codigo_referencia():
    error = parsear_error_servidor_nota_debito(400, "codigoReferencia: valor inválido")
    assert error.paso == 1
    assert error.campo == "codigo_referencia"


def test_400_razon():
    error = parsear_error_servidor_nota_debito(400, "razon: excede el largo máximo")
    assert error.paso == 1
    assert error.campo == "razon"


def test_400_lineas_va_a_paso2():
    error = parsear_error_servidor_nota_debito(400, "lineas[0].productoId: no existe")
    assert error.paso == 2
    assert error.campo is None


def test_400_desconocido_cae_a_paso1():
    error = parsear_error_servidor_nota_debito(400, "algo totalmente inesperado")
    assert error.paso == 1
    assert error.campo is None


def test_orden_de_prioridad_codigo_referencia_antes_que_razon():
    error = parsear_error_servidor_nota_debito(
        400, "codigoReferencia y razon inválidos"
    )
    assert error.campo == "codigo_referencia"
