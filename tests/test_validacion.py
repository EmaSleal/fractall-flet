import validacion


def test_password_valida_acepta_password_fuerte():
    assert validacion.password_valida("Abc123!!")


def test_password_valida_rechaza_sin_mayuscula():
    assert not validacion.password_valida("abc123!!")


def test_password_valida_rechaza_sin_numero():
    assert not validacion.password_valida("Abcdefg!")


def test_password_valida_rechaza_sin_caracter_especial():
    assert not validacion.password_valida("Abc12345")


def test_password_valida_rechaza_corta():
    assert not validacion.password_valida("Ab1!")


def test_email_valido():
    assert validacion.email_valido("usuario@fractall.app")
    assert not validacion.email_valido("no-es-un-correo")


def test_bloque_todo_o_nada_vacio_es_valido():
    assert validacion.bloque_todo_o_nada({"a": "", "b": "", "c": ""}) == {}


def test_bloque_todo_o_nada_completo_es_valido():
    assert validacion.bloque_todo_o_nada({"a": "1", "b": "2", "c": "3"}) == {}


def test_bloque_todo_o_nada_parcial_marca_los_vacios():
    errores = validacion.bloque_todo_o_nada({"a": "1", "b": "", "c": ""})
    assert set(errores.keys()) == {"b", "c"}
    assert "a" not in errores


def test_exoneracion_requiere_institucion_otros_si_tipo_99():
    assert validacion.exoneracion_requiere_institucion_otros("99", "") is not None
    assert validacion.exoneracion_requiere_institucion_otros("99", "  ") is not None


def test_exoneracion_no_requiere_institucion_otros_si_tipo_99_completo():
    assert validacion.exoneracion_requiere_institucion_otros("99", "Ministerio X") is None


def test_exoneracion_no_requiere_institucion_otros_si_otro_tipo():
    assert validacion.exoneracion_requiere_institucion_otros("01", "") is None
