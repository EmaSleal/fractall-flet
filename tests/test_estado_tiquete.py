from estado_factura import ExoneracionVigenteItem, LineaWizard
from estado_tiquete import EstadoTiquete


def test_estado_inicial():
    estado = EstadoTiquete()
    assert estado.paso == 1
    assert estado.cliente_id is None
    assert len(estado.lineas) == 1
    assert estado.condicion_venta == "01"
    assert estado.medio_pago == "01"
    assert estado.moneda == "CRC"
    assert estado.tipo_cambio == 1.0


def test_establecer_cliente_resetea_exoneraciones_y_lineas():
    estado = EstadoTiquete()
    estado.exoneraciones_vigentes = [ExoneracionVigenteItem(id="e-1", descripcion="X")]
    estado.lineas = [LineaWizard(exoneracion_id="e-1"), LineaWizard(exoneracion_id="e-1")]

    estado.establecer_cliente("c-2", "Otro cliente", "02 456")

    assert estado.cliente_id == "c-2"
    assert estado.exoneraciones_vigentes == []
    assert all(linea.exoneracion_id is None for linea in estado.lineas)


def test_quitar_cliente_limpia_todo():
    estado = EstadoTiquete()
    estado.establecer_cliente("c-1", "Ana", "01 123")
    estado.exoneraciones_vigentes = [ExoneracionVigenteItem(id="e-1", descripcion="X")]
    estado.lineas = [LineaWizard(exoneracion_id="e-1")]

    estado.quitar_cliente()

    assert estado.cliente_id is None
    assert estado.cliente_nombre is None
    assert estado.cliente_identificacion is None
    assert estado.exoneraciones_vigentes == []
    assert estado.lineas[0].exoneracion_id is None


def test_establecer_condicion_venta_limpia_campos_dependientes():
    estado = EstadoTiquete()
    estado.establecer_condicion_venta("02")
    estado.plazo_credito = 30
    estado.establecer_condicion_venta("01")
    assert estado.plazo_credito is None

    estado.establecer_condicion_venta("99")
    estado.condicion_venta_otros = "Detalle"
    estado.establecer_condicion_venta("01")
    assert estado.condicion_venta_otros == ""


def test_establecer_moneda_crc_fuerza_tipo_cambio_1():
    estado = EstadoTiquete()
    estado.establecer_moneda("USD")
    estado.tipo_cambio = 550.0
    estado.establecer_moneda("CRC")
    assert estado.tipo_cambio == 1.0


def test_agregar_y_quitar_linea():
    estado = EstadoTiquete()
    estado.agregar_linea()
    assert len(estado.lineas) == 2

    estado.quitar_linea(0)
    assert len(estado.lineas) == 1


def test_quitar_linea_no_deja_la_lista_vacia():
    estado = EstadoTiquete()
    estado.quitar_linea(0)
    assert len(estado.lineas) == 1


def test_a_cuerpo_creacion_sin_cliente_omite_clienteid():
    estado = EstadoTiquete()
    estado.lineas = [LineaWizard(producto_id="p-1", cantidad=1, precio_unitario=100)]

    cuerpo = estado.a_cuerpo_creacion()

    assert "clienteId" not in cuerpo
    assert cuerpo["condicionVenta"] == "01"
    assert cuerpo["medioPago"] == "01"
    assert cuerpo["moneda"] == "CRC"
    assert cuerpo["tipoCambio"] == 1.0
    assert cuerpo["lineas"][0] == {
        "productoId": "p-1",
        "cantidad": 1,
        "precioUnitario": 100,
    }


def test_a_cuerpo_creacion_con_cliente_incluye_clienteid():
    estado = EstadoTiquete()
    estado.establecer_cliente("c-1", "Ana", "01 123")
    estado.lineas = [LineaWizard(producto_id="p-1", cantidad=1, precio_unitario=100)]

    cuerpo = estado.a_cuerpo_creacion()

    assert cuerpo["clienteId"] == "c-1"


def test_a_cuerpo_creacion_omite_condicion_venta_otros_y_plazo_si_no_aplica():
    estado = EstadoTiquete()
    estado.lineas = [LineaWizard(producto_id="p-1", cantidad=1, precio_unitario=100)]

    cuerpo = estado.a_cuerpo_creacion()

    assert "plazoCredito" not in cuerpo
    assert "condicionVentaOtros" not in cuerpo


def test_a_cuerpo_creacion_incluye_condicion_credito():
    estado = EstadoTiquete()
    estado.establecer_condicion_venta("02")
    estado.plazo_credito = 30
    estado.lineas = [LineaWizard(producto_id="p-1", cantidad=1, precio_unitario=100)]

    cuerpo = estado.a_cuerpo_creacion()

    assert cuerpo["plazoCredito"] == 30


def test_a_cuerpo_creacion_incluye_condicion_otros():
    estado = EstadoTiquete()
    estado.establecer_condicion_venta("99")
    estado.condicion_venta_otros = "Detalle"
    estado.lineas = [LineaWizard(producto_id="p-1", cantidad=1, precio_unitario=100)]

    cuerpo = estado.a_cuerpo_creacion()

    assert cuerpo["condicionVentaOtros"] == "Detalle"


def test_a_cuerpo_creacion_moneda_crc_fuerza_tipo_cambio():
    estado = EstadoTiquete()
    estado.lineas = [LineaWizard(producto_id="p-1", cantidad=1, precio_unitario=100)]
    # simular estado inconsistente, igual criterio que test_estado_factura
    estado.moneda = "CRC"
    estado.tipo_cambio = 550.0

    cuerpo = estado.a_cuerpo_creacion()

    assert cuerpo["tipoCambio"] == 1.0


def test_a_cuerpo_creacion_medio_pago_no_crc():
    estado = EstadoTiquete()
    estado.establecer_moneda("USD")
    estado.tipo_cambio = 550.0
    estado.medio_pago = "02"
    estado.lineas = [LineaWizard(producto_id="p-1", cantidad=1, precio_unitario=100)]

    cuerpo = estado.a_cuerpo_creacion()

    assert cuerpo["medioPago"] == "02"
    assert cuerpo["tipoCambio"] == 550.0
