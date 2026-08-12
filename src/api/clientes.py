from dataclasses import dataclass
from typing import Any, Optional

from .cliente import ApiExito, ApiFallo, ApiResultado
from .cliente_autenticado import peticion_autenticada


@dataclass
class Cliente:
    id: str
    nombre: str
    tipo_identificacion: str
    numero_identificacion: str
    codigo_actividad: Optional[str]
    codigo_provincia: Optional[str]
    canton: Optional[str]
    distrito: Optional[str]
    otras_senas: Optional[str]
    telefono: Optional[str]
    email: Optional[str]
    requiere_factura_electronica: bool


def _cliente_desde(datos: dict) -> Cliente:
    return Cliente(
        id=datos["id"],
        nombre=datos.get("nombre", ""),
        tipo_identificacion=datos.get("tipoIdentificacion", ""),
        numero_identificacion=datos.get("numeroIdentificacion", ""),
        codigo_actividad=datos.get("codigoActividad"),
        codigo_provincia=datos.get("codigoProvincia"),
        canton=datos.get("canton"),
        distrito=datos.get("distrito"),
        otras_senas=datos.get("otrasSenas"),
        telefono=datos.get("telefono"),
        email=datos.get("email"),
        requiere_factura_electronica=datos.get("requiereFacturaElectronica", True),
    )


@dataclass
class PaginaClientes:
    items: list[Cliente]
    next_cursor: Optional[str]


async def listar_clientes(
    q: str = "", cursor: Optional[str] = None, limit: int = 20
) -> ApiResultado[PaginaClientes]:
    parametros: dict[str, Any] = {"limit": limit}
    if q:
        parametros["q"] = q
    if cursor:
        parametros["cursor"] = cursor

    resultado = await peticion_autenticada(
        "GET", "/catalogo/clientes", parametros=parametros
    )
    if isinstance(resultado, ApiFallo):
        return resultado

    datos = resultado.datos
    return ApiExito(
        datos=PaginaClientes(
            items=[_cliente_desde(c) for c in datos.get("items", [])],
            next_cursor=datos.get("nextCursor"),
        )
    )


async def buscar_clientes(q: str, limit: int = 10) -> ApiResultado[list[Cliente]]:
    """Versión aplanada de listar_clientes(), para el combobox de búsqueda
    en vivo del wizard de facturas (no necesita paginación, solo top N)."""
    resultado = await listar_clientes(q=q, limit=limit)
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(datos=resultado.datos.items)


async def obtener_cliente(id_cliente: str) -> ApiResultado[Optional[Cliente]]:
    resultado = await peticion_autenticada("GET", f"/catalogo/clientes/{id_cliente}")
    if isinstance(resultado, ApiFallo):
        if resultado.error.status == 404:
            return ApiExito(datos=None)
        return resultado
    return ApiExito(datos=_cliente_desde(resultado.datos))


@dataclass
class ActividadHacienda:
    codigo: str
    descripcion: str
    tipo: Optional[str]
    estado: Optional[str]


def _actividad_desde(datos: dict) -> ActividadHacienda:
    return ActividadHacienda(
        codigo=datos.get("codigo", ""),
        descripcion=datos.get("descripcion", ""),
        tipo=datos.get("tipo"),
        estado=datos.get("estado"),
    )


@dataclass
class ConsultaHacienda:
    exitosa: bool
    nombre: Optional[str]
    tipo_identificacion: Optional[str]
    actividades: list[ActividadHacienda]
    mensaje_error: Optional[str]


async def consultar_hacienda(identificacion: str) -> ApiResultado[ConsultaHacienda]:
    """GET /catalogo/clientes/consultar-hacienda -- delega en
    HaciendaApiService#consultarContribuyente del backend. Nunca convierte
    "no encontrado" en ApiFallo (a diferencia de buscar_cabys): viaja en
    ConsultaHacienda.exitosa=False, igual que en fractall-frontend, porque el
    llamador necesita distinguir "no encontrado" de un error real de red/HTTP."""
    resultado = await peticion_autenticada(
        "GET",
        "/catalogo/clientes/consultar-hacienda",
        parametros={"identificacion": identificacion},
    )
    if isinstance(resultado, ApiFallo):
        return resultado

    datos = resultado.datos
    return ApiExito(
        datos=ConsultaHacienda(
            exitosa=datos.get("exitosa", False),
            nombre=datos.get("nombre"),
            tipo_identificacion=datos.get("tipoIdentificacion"),
            actividades=[_actividad_desde(a) for a in (datos.get("actividades") or [])],
            mensaje_error=datos.get("mensajeError"),
        )
    )


def _nulo_si_vacio(valor: str) -> Optional[str]:
    valor = valor.strip()
    return valor or None


@dataclass
class DatosCliente:
    nombre: str
    tipo_identificacion: str
    numero_identificacion: str
    codigo_actividad: str = ""
    codigo_provincia: str = ""
    canton: str = ""
    distrito: str = ""
    otras_senas: str = ""
    telefono: str = ""
    email: str = ""
    requiere_factura_electronica: bool = True

    def a_cuerpo(self) -> dict:
        return {
            "nombre": self.nombre.strip(),
            "tipoIdentificacion": self.tipo_identificacion,
            "numeroIdentificacion": self.numero_identificacion.strip(),
            "codigoActividad": _nulo_si_vacio(self.codigo_actividad),
            "codigoProvincia": _nulo_si_vacio(self.codigo_provincia),
            "canton": _nulo_si_vacio(self.canton),
            "distrito": _nulo_si_vacio(self.distrito),
            "otrasSenas": _nulo_si_vacio(self.otras_senas),
            "telefono": _nulo_si_vacio(self.telefono),
            "email": _nulo_si_vacio(self.email),
            "requiereFacturaElectronica": self.requiere_factura_electronica,
        }


@dataclass
class ClienteCreado:
    id: str


async def crear_cliente(datos: DatosCliente) -> ApiResultado[ClienteCreado]:
    resultado = await peticion_autenticada(
        "POST", "/catalogo/clientes", cuerpo=datos.a_cuerpo()
    )
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(datos=ClienteCreado(id=resultado.datos["id"]))


async def actualizar_cliente(id_cliente: str, datos: DatosCliente) -> ApiResultado[None]:
    resultado = await peticion_autenticada(
        "PATCH", f"/catalogo/clientes/{id_cliente}", cuerpo=datos.a_cuerpo()
    )
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(datos=None)


@dataclass
class ClienteExoneracion:
    id: str
    cliente_id: str
    tipo_documento: str
    numero_documento: Optional[str]
    nombre_institucion: Optional[str]
    numero_articulo: Optional[str]
    inciso: Optional[str]
    nombre_institucion_otros: Optional[str]
    fecha_emision: str
    fecha_vencimiento: Optional[str]
    porcentaje_exoneracion: float
    activo: bool
    vigente: bool


def _exoneracion_desde(datos: dict) -> ClienteExoneracion:
    return ClienteExoneracion(
        id=datos["id"],
        cliente_id=datos.get("clienteId", ""),
        tipo_documento=datos.get("tipoDocumento", ""),
        numero_documento=datos.get("numeroDocumento"),
        nombre_institucion=datos.get("nombreInstitucion"),
        numero_articulo=datos.get("numeroArticulo"),
        inciso=datos.get("inciso"),
        nombre_institucion_otros=datos.get("nombreInstitucionOtros"),
        fecha_emision=datos.get("fechaEmision", ""),
        fecha_vencimiento=datos.get("fechaVencimiento"),
        porcentaje_exoneracion=datos.get("porcentajeExoneracion", 0),
        activo=datos.get("activo", False),
        vigente=datos.get("vigente", False),
    )


async def listar_exoneraciones(
    id_cliente: str, solo_vigentes: bool = False
) -> ApiResultado[list[ClienteExoneracion]]:
    resultado = await peticion_autenticada(
        "GET",
        f"/catalogo/clientes/{id_cliente}/exoneraciones",
        parametros={"soloVigentes": "true" if solo_vigentes else "false"},
    )
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(datos=[_exoneracion_desde(e) for e in resultado.datos])


@dataclass
class DatosExoneracion:
    tipo_documento: str
    numero_documento: str
    nombre_institucion: str
    fecha_emision: str
    porcentaje_exoneracion: float
    numero_articulo: str = ""
    inciso: str = ""
    nombre_institucion_otros: str = ""
    fecha_vencimiento: str = ""

    def a_cuerpo(self) -> dict:
        return {
            "tipoDocumento": self.tipo_documento,
            "numeroDocumento": self.numero_documento.strip(),
            "nombreInstitucion": self.nombre_institucion.strip(),
            "numeroArticulo": _nulo_si_vacio(self.numero_articulo),
            "inciso": _nulo_si_vacio(self.inciso),
            "nombreInstitucionOtros": _nulo_si_vacio(self.nombre_institucion_otros),
            "fechaEmision": self.fecha_emision,
            "fechaVencimiento": _nulo_si_vacio(self.fecha_vencimiento),
            "porcentajeExoneracion": self.porcentaje_exoneracion,
        }


async def crear_exoneracion(
    id_cliente: str, datos: DatosExoneracion
) -> ApiResultado[ClienteExoneracion]:
    resultado = await peticion_autenticada(
        "POST",
        f"/catalogo/clientes/{id_cliente}/exoneraciones",
        cuerpo=datos.a_cuerpo(),
    )
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(datos=_exoneracion_desde(resultado.datos))


async def desactivar_exoneracion(id_exoneracion: str) -> ApiResultado[None]:
    resultado = await peticion_autenticada(
        "POST", f"/catalogo/exoneraciones/{id_exoneracion}/desactivar"
    )
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(datos=None)
