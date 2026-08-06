from dataclasses import dataclass

from .cliente import ApiExito, ApiFallo, ApiResultado
from .cliente_autenticado import peticion_autenticada
from .errores import ErrorApi


@dataclass
class CabysResultado:
    codigo: str
    codigo_formateado: str
    descripcion: str
    impuesto: float


async def buscar_cabys(q: str, top: int = 10) -> ApiResultado[list[CabysResultado]]:
    """A diferencia de fractall-frontend (que pasa por un BFF Route Handler
    /api/catalogo/cabys), fractall-flet no tiene capa BFF: llama directo a
    GET /catalogo/cabys del backend, como el resto de los endpoints."""
    resultado = await peticion_autenticada(
        "GET", "/catalogo/cabys", parametros={"q": q, "top": top}
    )
    if isinstance(resultado, ApiFallo):
        return resultado

    datos = resultado.datos
    if not datos.get("exitosa", True):
        mensaje = datos.get("mensajeError") or "Error al buscar el código CABYS."
        return ApiFallo(error=ErrorApi(mensaje=mensaje, status=200))

    return ApiExito(
        datos=[
            CabysResultado(
                codigo=c["codigo"],
                codigo_formateado=c.get("codigoFormateado", c["codigo"]),
                descripcion=c.get("descripcion", ""),
                impuesto=c.get("impuesto", 0),
            )
            for c in datos.get("cabys", [])
        ]
    )
