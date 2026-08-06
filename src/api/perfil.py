from dataclasses import dataclass
from typing import Optional

from .cliente import ApiExito, ApiFallo, ApiResultado, peticion
from .cliente_autenticado import peticion_autenticada


@dataclass
class EmpresaResumen:
    empresa_id: str
    razon_social: str
    nombre_comercial: Optional[str]
    rol_codigo: Optional[str]
    estado_membresia: Optional[str]


def _empresa_resumen_desde(datos: dict) -> EmpresaResumen:
    return EmpresaResumen(
        empresa_id=datos["empresaId"],
        razon_social=datos.get("razonSocial", ""),
        nombre_comercial=datos.get("nombreComercial"),
        rol_codigo=datos.get("rolCodigo"),
        estado_membresia=datos.get("estadoMembresia"),
    )


@dataclass
class PerfilUsuario:
    usuario_id: str
    nombre: str
    email: str
    mfa_habilitado: bool
    empresa_activa: EmpresaResumen
    permisos: list[str]


async def obtener_mis_empresas(token: str) -> ApiResultado[list[EmpresaResumen]]:
    resultado = await peticion("GET", "/auth/mis-empresas", token=token)
    if isinstance(resultado, ApiFallo):
        return resultado

    return ApiExito(
        datos=[_empresa_resumen_desde(e) for e in resultado.datos]
    )


async def obtener_perfil() -> ApiResultado[PerfilUsuario]:
    """Usa la sesión guardada (con refresh automático), a diferencia de
    obtener_mis_empresas() que recibe un token de alcance mínimo explícito
    durante el flujo de selección de tenant, antes de que exista sesión."""
    resultado = await peticion_autenticada("GET", "/auth/perfil")
    if isinstance(resultado, ApiFallo):
        return resultado

    datos = resultado.datos
    return ApiExito(
        datos=PerfilUsuario(
            usuario_id=datos["usuarioId"],
            nombre=datos["nombre"],
            email=datos["email"],
            mfa_habilitado=datos["mfaHabilitado"],
            empresa_activa=_empresa_resumen_desde(datos["empresaActiva"]),
            permisos=datos.get("permisos", []),
        )
    )
