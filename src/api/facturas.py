from dataclasses import dataclass
from typing import Any, Optional

from .cliente import ApiExito, ApiFallo, ApiResultado, ArchivoDescargado
from .cliente_autenticado import peticion_autenticada, peticion_autenticada_binaria


@dataclass
class FacturaResumen:
    id: str
    consecutivo: str
    cliente_id: str
    cliente_nombre: str
    ambiente_hacienda: str
    moneda: str
    total: float
    estado: str
    ultimo_resultado_consulta: Optional[str]
    fecha_emision: str


def _factura_resumen_desde(datos: dict) -> FacturaResumen:
    return FacturaResumen(
        id=datos["id"],
        consecutivo=datos.get("consecutivo", ""),
        cliente_id=datos.get("clienteId", ""),
        cliente_nombre=datos.get("clienteNombre", ""),
        ambiente_hacienda=datos.get("ambienteHacienda", ""),
        moneda=datos.get("moneda", "CRC"),
        total=datos.get("total", 0),
        estado=datos.get("estado", "GENERADO"),
        ultimo_resultado_consulta=datos.get("ultimoResultadoConsulta"),
        fecha_emision=datos.get("fechaEmision", ""),
    )


@dataclass
class PaginaFacturas:
    items: list[FacturaResumen]
    next_cursor: Optional[str]


@dataclass
class DescuentoLinea:
    monto_descuento: float
    codigo_descuento: Optional[str]
    codigo_descuento_otro: Optional[str]
    naturaleza_descuento: Optional[str]


def _descuento_desde(datos: dict) -> DescuentoLinea:
    return DescuentoLinea(
        monto_descuento=datos.get("montoDescuento", 0),
        codigo_descuento=datos.get("codigoDescuento"),
        codigo_descuento_otro=datos.get("codigoDescuentoOtro"),
        naturaleza_descuento=datos.get("naturalezaDescuento"),
    )


@dataclass
class LineaFactura:
    id: str
    producto_id: str
    numero_linea: int
    cantidad: float
    precio_unitario: float
    subtotal: float
    codigo_cabys_aplicado: Optional[str]
    gravado_aplicado: bool
    porcentaje_impuesto_aplicado: float
    exoneracion_id: Optional[str]
    porcentaje_exoneracion_aplicado: Optional[float]
    monto_exoneracion_aplicado: Optional[float]
    unidad_medida_comercial: Optional[str]
    descuentos: list[DescuentoLinea]


def _linea_desde(datos: dict) -> LineaFactura:
    return LineaFactura(
        id=datos.get("id", ""),
        producto_id=datos.get("productoId", ""),
        numero_linea=datos.get("numeroLinea", 0),
        cantidad=datos.get("cantidad", 0),
        precio_unitario=datos.get("precioUnitario", 0),
        subtotal=datos.get("subtotal", 0),
        codigo_cabys_aplicado=datos.get("codigoCabysAplicado"),
        gravado_aplicado=datos.get("gravadoAplicado", False),
        porcentaje_impuesto_aplicado=datos.get("porcentajeImpuestoAplicado", 0),
        exoneracion_id=datos.get("exoneracionId"),
        porcentaje_exoneracion_aplicado=datos.get("porcentajeExoneracionAplicado"),
        monto_exoneracion_aplicado=datos.get("montoExoneracionAplicado"),
        unidad_medida_comercial=datos.get("unidadMedidaComercial"),
        descuentos=[_descuento_desde(d) for d in datos.get("descuentos", [])],
    )


@dataclass
class MedioPagoFactura:
    orden: int
    tipo_medio_pago: str
    medio_pago_otros: Optional[str]
    total_medio_pago: float


def _medio_pago_desde(datos: dict) -> MedioPagoFactura:
    return MedioPagoFactura(
        orden=datos.get("orden", 0),
        tipo_medio_pago=datos.get("tipoMedioPago", ""),
        medio_pago_otros=datos.get("medioPagoOtros"),
        total_medio_pago=datos.get("totalMedioPago", 0),
    )


@dataclass
class OtroCargoFactura:
    orden: int
    tipo_documento_oc: str
    tipo_documento_otros: Optional[str]
    identidad_tipo: Optional[str]
    identidad_numero: Optional[str]
    nombre_tercero: Optional[str]
    detalle: Optional[str]
    monto_cargo: float


def _otro_cargo_desde(datos: dict) -> OtroCargoFactura:
    return OtroCargoFactura(
        orden=datos.get("orden", 0),
        tipo_documento_oc=datos.get("tipoDocumentoOc", ""),
        tipo_documento_otros=datos.get("tipoDocumentoOtros"),
        identidad_tipo=datos.get("identidadTipo"),
        identidad_numero=datos.get("identidadNumero"),
        nombre_tercero=datos.get("nombreTercero"),
        detalle=datos.get("detalle"),
        monto_cargo=datos.get("montoCargo", 0),
    )


@dataclass
class FacturaDetalle:
    id: str
    cliente_id: str
    cliente_nombre: str
    subtotal: float
    total_impuesto: float
    total: float
    lineas: list[LineaFactura]
    comprobante_id: Optional[str]
    ambiente_hacienda: str
    tipo_comprobante: str
    consecutivo: str
    clave_numerica: str
    estado: str
    fecha_emision: str
    condicion_venta_otros: Optional[str]
    total_iva_devuelto: Optional[float]
    otros_cargos: list[OtroCargoFactura]
    medios_pago: list[MedioPagoFactura]
    codigo_respuesta: Optional[str]
    mensaje_respuesta: Optional[str]
    fecha_respuesta: Optional[str]
    ultimo_resultado_consulta: Optional[str]
    intentos_envio: Optional[int]
    # FacturaResponse del backend NO trae `moneda` (gap conocido, también
    # presente en fractall-frontend con el mismo comentario) — se asume
    # CRC como fallback hasta que el backend lo exponga.
    moneda: str = "CRC"


def _factura_detalle_desde(datos: dict) -> FacturaDetalle:
    return FacturaDetalle(
        id=datos["id"],
        cliente_id=datos.get("clienteId", ""),
        cliente_nombre=datos.get("clienteNombre", ""),
        subtotal=datos.get("subtotal", 0),
        total_impuesto=datos.get("totalImpuesto", 0),
        total=datos.get("total", 0),
        lineas=[_linea_desde(x) for x in datos.get("lineas", [])],
        comprobante_id=datos.get("comprobanteId"),
        ambiente_hacienda=datos.get("ambienteHacienda", ""),
        tipo_comprobante=datos.get("tipoComprobante", ""),
        consecutivo=datos.get("consecutivo", ""),
        clave_numerica=datos.get("claveNumerica", ""),
        estado=datos.get("estado", "GENERADO"),
        fecha_emision=datos.get("fechaEmision", ""),
        condicion_venta_otros=datos.get("condicionVentaOtros"),
        total_iva_devuelto=datos.get("totalIvaDevuelto"),
        otros_cargos=[_otro_cargo_desde(x) for x in datos.get("otrosCargos", [])],
        medios_pago=[_medio_pago_desde(x) for x in datos.get("mediosPago", [])],
        codigo_respuesta=datos.get("codigoRespuesta"),
        mensaje_respuesta=datos.get("mensajeRespuesta"),
        fecha_respuesta=datos.get("fechaRespuesta"),
        ultimo_resultado_consulta=datos.get("ultimoResultadoConsulta"),
        intentos_envio=datos.get("intentosEnvio"),
    )


async def listar_facturas(
    estado: str = "",
    cliente_id: str = "",
    desde: str = "",
    hasta: str = "",
    cursor: Optional[str] = None,
    limit: int = 20,
) -> ApiResultado[PaginaFacturas]:
    parametros: dict[str, Any] = {"limit": limit}
    if estado:
        parametros["estado"] = estado
    if cliente_id:
        parametros["clienteId"] = cliente_id
    if desde:
        parametros["desde"] = desde
    if hasta:
        parametros["hasta"] = hasta
    if cursor:
        parametros["cursor"] = cursor

    resultado = await peticion_autenticada("GET", "/facturas", parametros=parametros)
    if isinstance(resultado, ApiFallo):
        return resultado

    datos = resultado.datos
    return ApiExito(
        datos=PaginaFacturas(
            items=[_factura_resumen_desde(f) for f in datos.get("items", [])],
            next_cursor=datos.get("nextCursor"),
        )
    )


async def crear_factura(cuerpo: dict) -> ApiResultado[FacturaDetalle]:
    """`cuerpo` viene de `EstadoFactura.a_cuerpo_creacion()` — esta función
    se mantiene deliberadamente ajena a los conceptos del wizard (no
    importa EstadoFactura), es solo la capa de contrato HTTP."""
    resultado = await peticion_autenticada("POST", "/facturas", cuerpo=cuerpo)
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(datos=_factura_detalle_desde(resultado.datos))


async def obtener_factura(id_factura: str) -> ApiResultado[Optional[FacturaDetalle]]:
    resultado = await peticion_autenticada("GET", f"/facturas/{id_factura}")
    if isinstance(resultado, ApiFallo):
        if resultado.error.status == 404:
            return ApiExito(datos=None)
        return resultado
    return ApiExito(datos=_factura_detalle_desde(resultado.datos))


async def reenviar_factura(id_factura: str) -> ApiResultado[FacturaDetalle]:
    resultado = await peticion_autenticada("POST", f"/facturas/{id_factura}/reenviar")
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(datos=_factura_detalle_desde(resultado.datos))


async def descargar_pdf(id_factura: str) -> ApiResultado[ArchivoDescargado]:
    return await peticion_autenticada_binaria("GET", f"/facturas/{id_factura}/pdf")


async def descargar_xml_factura(id_factura: str) -> ApiResultado[ArchivoDescargado]:
    return await peticion_autenticada_binaria(
        "GET", f"/facturas/{id_factura}/xml/factura"
    )


async def descargar_xml_respuesta(id_factura: str) -> ApiResultado[ArchivoDescargado]:
    return await peticion_autenticada_binaria(
        "GET", f"/facturas/{id_factura}/xml/respuesta"
    )
