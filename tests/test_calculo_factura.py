import calculo_factura as calc
from estado_factura import LineaWizard, MedioPagoWizard, OtroCargoWizard


def test_a_centavos_redondea_como_math_round_de_js():
    # 0.125 * 100 == 12.5 exacto en binario — round() de Python (banker's
    # rounding) da 12; Math.round de JS (y nuestro a_centavos) da 13.
    assert calc.a_centavos(0.125) == 13
    assert round(0.125 * 100) == 12  # confirma que la diferencia es real
    assert calc.a_centavos(10.0) == 1000
    assert calc.a_centavos(0.1) == 10


def test_calcular_subtotal_linea():
    assert calc.calcular_subtotal_linea(cantidad=2, precio_unitario=100, descuento_monto=10) == 190


def test_calcular_iva_linea():
    assert calc.calcular_iva_linea(
        cantidad=2, precio_unitario=100, descuento_monto=0, porcentaje_impuesto=13
    ) == 26.0


def test_calcular_subtotal_y_total_factura():
    lineas = [
        LineaWizard(cantidad=2, precio_unitario=100, porcentaje_impuesto=13, descuento_monto=0),
        LineaWizard(cantidad=1, precio_unitario=50, porcentaje_impuesto=13, descuento_monto=0),
    ]
    assert calc.calcular_subtotal_factura(lineas) == 250
    assert round(calc.calcular_iva_total(lineas), 2) == 32.5
    assert round(calc.calcular_total_factura(lineas), 2) == 282.5


def test_calcular_total_factura_incluye_otros_cargos():
    lineas = [LineaWizard(cantidad=1, precio_unitario=100, porcentaje_impuesto=0)]
    cargos = [OtroCargoWizard(monto_cargo=50)]
    assert calc.calcular_total_factura(lineas, cargos) == 150


def test_coincide_total_medios_pago_exacto():
    lineas = [LineaWizard(cantidad=1, precio_unitario=100, porcentaje_impuesto=13)]
    total = calc.calcular_total_factura(lineas)  # 113.0
    medios = [MedioPagoWizard(total_medio_pago=113.0)]
    assert calc.coincide_total_medios_pago(medios, total) is True


def test_coincide_total_medios_pago_evita_drift_de_floats():
    # 0.1 + 0.2 != 0.3 en floats crudos — la comparación en centavos debe
    # seguir funcionando igual.
    medios = [MedioPagoWizard(total_medio_pago=0.1), MedioPagoWizard(total_medio_pago=0.2)]
    assert calc.coincide_total_medios_pago(medios, 0.3) is True


def test_no_coincide_total_medios_pago_si_falta_plata():
    lineas = [LineaWizard(cantidad=1, precio_unitario=100, porcentaje_impuesto=13)]
    total = calc.calcular_total_factura(lineas)
    medios = [MedioPagoWizard(total_medio_pago=100.0)]
    assert calc.coincide_total_medios_pago(medios, total) is False


def test_calcular_delta_medios_pago():
    lineas = [LineaWizard(cantidad=1, precio_unitario=100, porcentaje_impuesto=0)]
    total = calc.calcular_total_factura(lineas)  # 100
    medios = [MedioPagoWizard(total_medio_pago=120.0)]
    assert calc.calcular_delta_medios_pago(medios, total) == 20.0
