from dataclasses import dataclass
from typing import Optional

from .cliente import ApiExito, ApiFallo, ApiResultado
from .cliente_autenticado import peticion_autenticada


@dataclass
class Empresa:
    id: str
    razon_social: Optional[str]
    nombre_comercial: Optional[str]
    numero_identificacion: Optional[str]
    tipo_identificacion: Optional[str]
    codigo_actividad: Optional[str]
    codigo_provincia: Optional[str]
    canton: Optional[str]
    distrito: Optional[str]
    barrio: Optional[str]
    otras_senas: Optional[str]
    telefono: Optional[str]
    email: Optional[str]
    ambiente_hacienda: Optional[str]
    status: str
    tiene_certificado: bool


def _empresa_desde(datos: dict) -> Empresa:
    return Empresa(
        id=datos["id"],
        razon_social=datos.get("razonSocial"),
        nombre_comercial=datos.get("nombreComercial"),
        numero_identificacion=datos.get("numeroIdentificacion"),
        tipo_identificacion=datos.get("tipoIdentificacion"),
        codigo_actividad=datos.get("codigoActividad"),
        codigo_provincia=datos.get("codigoProvincia"),
        canton=datos.get("canton"),
        distrito=datos.get("distrito"),
        barrio=datos.get("barrio"),
        otras_senas=datos.get("otrasSenas"),
        telefono=datos.get("telefono"),
        email=datos.get("email"),
        ambiente_hacienda=datos.get("ambienteHacienda"),
        status=datos.get("status", "REGISTRADA"),
        tiene_certificado=datos.get("tieneCertificado", False),
    )


async def obtener_empresa() -> ApiResultado[Empresa]:
    resultado = await peticion_autenticada("GET", "/empresa")
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(datos=_empresa_desde(resultado.datos))


def _nulo_si_vacio(valor: str) -> Optional[str]:
    valor = valor.strip()
    return valor or None


@dataclass
class DatosFiscales:
    razon_social: str = ""
    nombre_comercial: str = ""
    numero_identificacion: str = ""
    tipo_identificacion: str = ""
    codigo_actividad: str = ""
    codigo_provincia: str = ""
    canton: str = ""
    distrito: str = ""
    barrio: str = ""
    otras_senas: str = ""
    telefono: str = ""
    email: str = ""

    def a_cuerpo(self) -> dict:
        return {
            "razonSocial": _nulo_si_vacio(self.razon_social),
            "nombreComercial": _nulo_si_vacio(self.nombre_comercial),
            "numeroIdentificacion": _nulo_si_vacio(self.numero_identificacion),
            "tipoIdentificacion": _nulo_si_vacio(self.tipo_identificacion),
            "codigoActividad": _nulo_si_vacio(self.codigo_actividad),
            "codigoProvincia": _nulo_si_vacio(self.codigo_provincia),
            "canton": _nulo_si_vacio(self.canton),
            "distrito": _nulo_si_vacio(self.distrito),
            "barrio": _nulo_si_vacio(self.barrio),
            "otrasSenas": _nulo_si_vacio(self.otras_senas),
            "telefono": _nulo_si_vacio(self.telefono),
            "email": _nulo_si_vacio(self.email),
        }


async def actualizar_datos_fiscales(datos: DatosFiscales) -> ApiResultado[Empresa]:
    resultado = await peticion_autenticada("PATCH", "/empresa", cuerpo=datos.a_cuerpo())
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(datos=_empresa_desde(resultado.datos))


async def cargar_certificado(
    nombre_archivo: str, contenido: bytes, pin: str
) -> ApiResultado[None]:
    resultado = await peticion_autenticada(
        "POST",
        "/empresa/certificado",
        archivos={"certificado": (nombre_archivo, contenido, "application/x-pkcs12")},
        datos_formulario={"pin": pin},
    )
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(datos=None)


async def configurar_credenciales_hacienda(
    usuario: str, password: str, ambiente: str
) -> ApiResultado[None]:
    resultado = await peticion_autenticada(
        "POST",
        "/empresa/credenciales-hacienda",
        cuerpo={
            "usuarioHacienda": usuario,
            "password": password,
            "ambiente": ambiente,
        },
    )
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(datos=None)


async def cambiar_ambiente(ambiente: str) -> ApiResultado[None]:
    resultado = await peticion_autenticada(
        "PATCH", "/empresa/ambiente", cuerpo={"ambiente": ambiente}
    )
    if isinstance(resultado, ApiFallo):
        return resultado
    return ApiExito(datos=None)
