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


# Cantidad de caracteres esperada de numeroIdentificacion por tipo -- espejo de
# TipoIdentificacion#validarNumero en el backend (01 Física=9, 02 Jurídica=10, 03 DIMEX=11 o
# 12, 04 NITE=10). Deliberadamente NO se exige que sean solo dígitos: Hacienda podría estar
# migrando la cédula jurídica a un formato alfanumérico (Decreto 44648-MJ), todavía sin
# confirmar en el documento técnico oficial vigente -- ver fractall/docs/referencia. Solo se
# valida la cantidad de caracteres, que no depende de esa incertidumbre (mismo criterio ya
# aplicado en fractall-frontend).
LONGITUDES_IDENTIFICACION: dict[str, tuple[int, ...]] = {
    "01": (9,),
    "02": (10,),
    "03": (11, 12),
    "04": (10,),
}


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

TIPOS_COMPROBANTE = [
    ("01", "Factura Electrónica"),
    ("02", "Nota de Débito Electrónica"),
    ("03", "Nota de Crédito Electrónica"),
    ("04", "Tiquete Electrónico"),
    ("05", "Confirmación de aceptación del comprobante"),
    ("06", "Confirmación de aceptación parcial del comprobante"),
    ("07", "Confirmación de rechazo del comprobante"),
    ("08", "Factura Electrónica de Compra"),
    ("09", "Factura Electrónica de Exportación"),
    ("10", "Recibo Electrónico de Pago"),
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


def label_tipo_comprobante(codigo: str) -> str:
    return dict(TIPOS_COMPROBANTE).get(codigo, codigo)


def label_tipo_documento_oc(codigo: str) -> str:
    return dict(TIPOS_DOCUMENTO_OC).get(codigo, codigo)


CODIGOS_REFERENCIA = [
    ("01", "Anula documento de referencia"),
    ("02", "Corrige texto de documento de referencia"),
    ("04", "Referencia a otro documento"),
    ("05", "Sustituye comprobante provisional por contingencia"),
    ("06", "Devolución de mercancía"),
    ("07", "Sustituye comprobante electrónico"),
    ("08", "Factura endosada"),
    ("09", "Nota de crédito financiera"),
    ("10", "Nota de débito financiera"),
    ("11", "Proveedor no domiciliado"),
    ("12", "Crédito por exoneración posterior a la facturación"),
    ("99", "Otros"),
]


def label_codigo_referencia(codigo: str) -> str:
    return dict(CODIGOS_REFERENCIA).get(codigo, codigo)
