from parsear_error_servidor_nota_credito import parsear_error_servidor_nota_credito


def test_404_va_a_paso1_con_mensaje_propio():
    error = parsear_error_servidor_nota_credito(404, "irrelevante")
    assert error.paso == 1
    assert error.campo is None
    assert "no se encontró" in error.mensaje


def test_409_factura_origen_no_aceptada_va_a_paso1_sin_interpretar_el_mensaje():
    error = parsear_error_servidor_nota_credito(
        409, "La factura de referencia f-1 no está en estado ACEPTADO (estado actual: RECHAZADO)"
    )
    assert error.paso == 1
    assert error.campo is None
    assert error.mensaje == (
        "La factura de referencia f-1 no está en estado ACEPTADO (estado actual: RECHAZADO)"
    )


def test_409_monto_excede_origen_va_a_paso2_sin_interpretar_el_mensaje():
    mensaje = (
        "El monto de las Notas de Crédito (100 previas + 50 actual) excede el total de "
        "la factura origen f-1 (120)"
    )
    error = parsear_error_servidor_nota_credito(409, mensaje)
    assert error.paso == 2
    assert error.campo is None
    assert error.mensaje == mensaje


def test_409_desconocido_cae_a_paso1():
    error = parsear_error_servidor_nota_credito(409, "otra regla de negocio no identificada")
    assert error.paso == 1
    assert error.campo is None


def test_400_cantidad_acreditada_excede_origen_va_a_paso2():
    error = parsear_error_servidor_nota_credito(
        400, "La cantidad acreditada (5) para la línea l-1 excede la cantidad de la línea origen (3)"
    )
    assert error.paso == 2
    assert error.campo is None


def test_400_linea_no_pertenece_a_la_factura_va_a_paso2():
    error = parsear_error_servidor_nota_credito(
        400, "La línea l-1 no pertenece a la factura de referencia f-1"
    )
    assert error.paso == 2
    assert error.campo is None


def test_400_codigo_referencia():
    error = parsear_error_servidor_nota_credito(400, "codigoReferencia: valor inválido")
    assert error.paso == 1
    assert error.campo == "codigo_referencia"


def test_400_razon():
    error = parsear_error_servidor_nota_credito(400, "razon: excede el largo máximo")
    assert error.paso == 1
    assert error.campo == "razon"


def test_400_lineas_va_a_paso2():
    error = parsear_error_servidor_nota_credito(400, "lineas[0]: debe tener al menos un elemento")
    assert error.paso == 2
    assert error.campo is None


def test_400_desconocido_cae_a_paso1():
    error = parsear_error_servidor_nota_credito(400, "algo totalmente inesperado")
    assert error.paso == 1
    assert error.campo is None


def test_orden_de_prioridad_codigo_referencia_antes_que_razon():
    error = parsear_error_servidor_nota_credito(400, "codigoReferencia y razon inválidos")
    assert error.campo == "codigo_referencia"
