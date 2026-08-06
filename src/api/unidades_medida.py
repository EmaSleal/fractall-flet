from dataclasses import dataclass

from .cliente import ApiExito, ApiFallo, ApiResultado
from .cliente_autenticado import peticion_autenticada


@dataclass
class UnidadMedida:
    codigo: str
    descripcion: str


async def listar_unidades_medida() -> ApiResultado[list[UnidadMedida]]:
    resultado = await peticion_autenticada("GET", "/catalogo/unidades-medida")
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(
        datos=[
            UnidadMedida(codigo=u["codigo"], descripcion=u.get("descripcion", ""))
            for u in resultado.datos
        ]
    )
