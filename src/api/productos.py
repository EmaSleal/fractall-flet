from dataclasses import dataclass
from typing import Any, Optional

from .cliente import ApiExito, ApiFallo, ApiResultado
from .cliente_autenticado import peticion_autenticada


@dataclass
class Producto:
    id: str
    codigo: str
    descripcion: str
    codigo_cabys: Optional[str]
    descripcion_cabys: Optional[str]
    cabys_validado_en: Optional[str]
    codigo_unidad_fe: Optional[str]
    precio_venta: float
    gravado: bool
    porcentaje_impuesto: float
    activo: bool


def _producto_desde(datos: dict) -> Producto:
    return Producto(
        id=datos["id"],
        codigo=datos.get("codigo", ""),
        descripcion=datos.get("descripcion", ""),
        codigo_cabys=datos.get("codigoCabys"),
        descripcion_cabys=datos.get("descripcionCabys"),
        cabys_validado_en=datos.get("cabysValidadoEn"),
        codigo_unidad_fe=datos.get("codigoUnidadFe"),
        precio_venta=datos.get("precioVenta", 0),
        gravado=datos.get("gravado", False),
        porcentaje_impuesto=datos.get("porcentajeImpuesto", 0),
        activo=datos.get("activo", True),
    )


@dataclass
class PaginaProductos:
    items: list[Producto]
    next_cursor: Optional[str]


async def listar_productos(
    activo: Optional[bool] = True,
    cursor: Optional[str] = None,
    limit: int = 20,
    q: str = "",
) -> ApiResultado[PaginaProductos]:
    """`activo` siempre se manda explícito (True o False) — el backend usa
    default=true cuando el parámetro está ausente, así que un "Todos" que
    omita el filtro terminaría mostrando solo activos igual que "Activos"
    (ese es justamente el bug que tiene fractall-frontend: su botón "Todos"
    no manda `activo` y por lo tanto no muestra realmente todos). Acá no
    se ofrece un "Todos" falso — solo Activos/Inactivos, explícitos."""
    parametros: dict[str, Any] = {"limit": limit, "activo": activo}
    if cursor:
        parametros["cursor"] = cursor
    if q:
        parametros["q"] = q

    resultado = await peticion_autenticada(
        "GET", "/catalogo/productos", parametros=parametros
    )
    if isinstance(resultado, ApiFallo):
        return resultado

    datos = resultado.datos
    return ApiExito(
        datos=PaginaProductos(
            items=[_producto_desde(p) for p in datos.get("items", [])],
            next_cursor=datos.get("nextCursor"),
        )
    )


async def buscar_productos(q: str, limit: int = 10) -> ApiResultado[list[Producto]]:
    """Versión aplanada para el combobox de líneas de factura — fuerza
    activo=True (un producto inactivo no debería poder facturarse), mismo
    criterio que el BFF /api/catalogo/productos del frontend."""
    resultado = await listar_productos(activo=True, q=q, limit=limit)
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(datos=resultado.datos.items)


async def obtener_producto(id_producto: str) -> ApiResultado[Optional[Producto]]:
    resultado = await peticion_autenticada("GET", f"/catalogo/productos/{id_producto}")
    if isinstance(resultado, ApiFallo):
        if resultado.error.status == 404:
            return ApiExito(datos=None)
        return resultado
    return ApiExito(datos=_producto_desde(resultado.datos))


def _nulo_si_vacio(valor: str) -> Optional[str]:
    valor = valor.strip()
    return valor or None


@dataclass
class DatosProducto:
    codigo: str
    descripcion: str
    codigo_cabys: str
    codigo_unidad_fe: str = ""
    precio_venta: float = 0.0
    activo: bool = True

    def a_cuerpo(self) -> dict:
        return {
            "codigo": self.codigo.strip(),
            "descripcion": self.descripcion.strip(),
            "codigoCabys": self.codigo_cabys.strip(),
            "codigoUnidadFe": _nulo_si_vacio(self.codigo_unidad_fe),
            "precioVenta": self.precio_venta,
            "activo": self.activo,
        }


@dataclass
class ProductoCreado:
    id: str


async def crear_producto(datos: DatosProducto) -> ApiResultado[ProductoCreado]:
    resultado = await peticion_autenticada(
        "POST", "/catalogo/productos", cuerpo=datos.a_cuerpo()
    )
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(datos=ProductoCreado(id=resultado.datos["id"]))


async def actualizar_producto(id_producto: str, datos: DatosProducto) -> ApiResultado[None]:
    resultado = await peticion_autenticada(
        "PATCH", f"/catalogo/productos/{id_producto}", cuerpo=datos.a_cuerpo()
    )
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(datos=None)


async def alternar_activo(id_producto: str, activo: bool) -> ApiResultado[None]:
    resultado = await peticion_autenticada(
        "PATCH", f"/catalogo/productos/{id_producto}", cuerpo={"activo": activo}
    )
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(datos=None)
