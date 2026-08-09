from dataclasses import dataclass

from .cliente import ApiExito, ApiFallo, ApiResultado
from .cliente_autenticado import peticion_autenticada


@dataclass
class Provincia:
    codigo: str
    nombre: str


@dataclass
class Canton:
    provincia_codigo: str
    codigo: str
    nombre: str


@dataclass
class Distrito:
    provincia_codigo: str
    canton_codigo: str
    codigo: str
    nombre: str


async def listar_provincias() -> ApiResultado[list[Provincia]]:
    resultado = await peticion_autenticada("GET", "/catalogo/ubicacion/provincias")
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(
        datos=[Provincia(codigo=p["codigo"], nombre=p["nombre"]) for p in resultado.datos]
    )


async def listar_cantones(provincia_codigo: str) -> ApiResultado[list[Canton]]:
    resultado = await peticion_autenticada(
        "GET", f"/catalogo/ubicacion/provincias/{provincia_codigo}/cantones"
    )
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(
        datos=[
            Canton(provincia_codigo=c["provinciaCodigo"], codigo=c["codigo"], nombre=c["nombre"])
            for c in resultado.datos
        ]
    )


async def listar_distritos(provincia_codigo: str, canton_codigo: str) -> ApiResultado[list[Distrito]]:
    resultado = await peticion_autenticada(
        "GET", f"/catalogo/ubicacion/cantones/{provincia_codigo}/{canton_codigo}/distritos"
    )
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(
        datos=[
            Distrito(
                provincia_codigo=d["provinciaCodigo"],
                canton_codigo=d["cantonCodigo"],
                codigo=d["codigo"],
                nombre=d["nombre"],
            )
            for d in resultado.datos
        ]
    )
