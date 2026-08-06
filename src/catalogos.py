"""Catálogos hardcodeados portados de fractall-frontend — ninguno viene de
un endpoint del backend, confirmado revisando el openapi.json completo."""

TIPOS_IDENTIFICACION = [
    ("01", "Cédula Física"),
    ("02", "Cédula Jurídica"),
    ("03", "DIMEX"),
    ("04", "NITE"),
]

_LABELS_TIPO_IDENTIFICACION = dict(TIPOS_IDENTIFICACION)


def label_tipo_identificacion(codigo: str) -> str:
    return _LABELS_TIPO_IDENTIFICACION.get(codigo, codigo)


# (valor, etiqueta, no_aplica_a_factura_electronica)
TIPOS_EXONERACION = [
    ("01", "Compras autorizadas por la DGT", True),
    ("02", "Ventas exentas a diplomáticos", False),
    ("03", "Autorizado por Ley especial", False),
    ("04", "Exenciones DGH — Autorización Local", False),
    ("05", "Exenciones DGH — Transitorio V", True),
    ("06", "Servicios turísticos ICT", True),
    ("07", "Transitorio XVII (reciclaje)", True),
    ("08", "Exoneración a Zona Franca", False),
    ("09", "Servicios complementarios exportación", False),
    ("10", "Órgano corporaciones municipales", False),
    ("11", "Exenciones DGH — Autorización Impuesto Local", False),
    ("99", "Otros", False),
]

_LABELS_TIPO_EXONERACION = {valor: etiqueta for valor, etiqueta, _ in TIPOS_EXONERACION}
_NO_APLICA_TIPO_EXONERACION = {valor: no_aplica for valor, _, no_aplica in TIPOS_EXONERACION}


def label_tipo_exoneracion(codigo: str) -> str:
    etiqueta = _LABELS_TIPO_EXONERACION.get(codigo, codigo)
    sufijo = " — (no aplica a FE)" if _NO_APLICA_TIPO_EXONERACION.get(codigo) else ""
    return f"{codigo} — {etiqueta}{sufijo}"


# Estados de empresa.status (GET /empresa) — no es un enum en el OpenAPI
# (el campo es "type": "string" genérico), son los 7 valores conocidos hoy
# vistos en fractall-frontend. Categoría usada para elegir el color del
# badge: "pendiente" | "aceptado" | "rechazado" | "neutral".
ESTADOS_EMPRESA = {
    "REGISTRADA": ("Registrada", "neutral"),
    "DATOS_FISCALES_INCOMPLETOS": ("Datos fiscales incompletos", "pendiente"),
    "CERTIFICADO_PENDIENTE": ("Certificado pendiente", "pendiente"),
    "CREDENCIALES_HACIENDA_PENDIENTES": ("Credenciales de Hacienda pendientes", "pendiente"),
    "HABILITADA": ("Habilitada", "aceptado"),
    "SUSPENDIDA": ("Suspendida", "rechazado"),
    "BAJA": ("De baja", "rechazado"),
}

# Estados en los que se ocultan ambiente/credenciales/certificado —
# no tiene sentido configurar Hacienda para una empresa suspendida/de baja.
ESTADOS_ADMINISTRATIVOS = {"SUSPENDIDA", "BAJA"}


def info_estado_empresa(status: str) -> tuple[str, str]:
    return ESTADOS_EMPRESA.get(status, ESTADOS_EMPRESA["REGISTRADA"])


AMBIENTES_HACIENDA = [
    ("SANDBOX", "Sandbox (pruebas)"),
    ("PRODUCCION", "Producción"),
]

CONDICIONES_VENTA = [
    ("01", "Contado"),
    ("02", "Crédito"),
    ("03", "Consignación"),
    ("04", "Apartado"),
    ("05", "Arrendamiento con opción de compra"),
    ("06", "Arrendamiento en función financiera"),
    ("99", "Otros"),
]

MONEDAS = [
    ("CRC", "Colones (CRC)"),
    ("USD", "Dólares (USD)"),
]

TIPOS_MEDIO_PAGO = [
    ("01", "Efectivo"),
    ("02", "Tarjeta"),
    ("03", "Cheque"),
    ("04", "Transferencia / depósito bancario"),
    ("05", "Recaudado por terceros"),
    ("06", "SINPE Móvil"),
    ("07", "Plataforma digital"),
    ("99", "Otros"),
]

TIPOS_DOCUMENTO_OC = [
    ("01", "Deuda"),
    ("02", "Anticipo"),
    ("03", "Transporte"),
    ("04", "Seguro"),
    ("05", "Intereses"),
    ("06", "Servicios"),
    ("07", "Productos"),
    ("08", "Otros cargos no gravados"),
    ("09", "Descuentos"),
    ("10", "Comisiones"),
    ("99", "Otros"),
]

# Estados de FacturaResponse.estado — el OpenAPI lo tipa como "string" libre,
# no enum, así que estos 5 son los valores de dominio conocidos hoy (mismo
# criterio que ESTADOS_EMPRESA). icono = nombre de ft.Icons, categoria elige
# el color (aceptado/pendiente/rechazado/neutral).
ESTADOS_FACTURA = {
    "GENERADO": ("Generado", "DESCRIPTION", "neutral"),
    "FIRMADO": ("Firmado", "DESCRIPTION", "neutral"),
    "ENVIADO": ("Enviado", "SCHEDULE", "pendiente"),
    "ACEPTADO": ("Aceptado", "CHECK_CIRCLE", "aceptado"),
    "RECHAZADO": ("Rechazado", "CANCEL", "rechazado"),
}


def info_estado_factura(estado: str) -> tuple[str, str, str]:
    return ESTADOS_FACTURA.get(estado, ESTADOS_FACTURA["GENERADO"])


def label_condicion_venta(codigo: str) -> str:
    return dict(CONDICIONES_VENTA).get(codigo, codigo)


def label_tipo_medio_pago(codigo: str) -> str:
    return dict(TIPOS_MEDIO_PAGO).get(codigo, codigo)


def label_tipo_documento_oc(codigo: str) -> str:
    return dict(TIPOS_DOCUMENTO_OC).get(codigo, codigo)
