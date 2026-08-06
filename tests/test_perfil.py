import api.perfil as perfil_module
from api.cliente import ApiExito, ApiFallo
from api.errores import ErrorApi
from api.perfil import EmpresaResumen, PerfilUsuario, obtener_mis_empresas, obtener_perfil


def _mockear_peticion(monkeypatch, resultado):
    async def _fake(*args, **kwargs):
        return resultado

    monkeypatch.setattr(perfil_module, "peticion", _fake)


def _mockear_peticion_autenticada(monkeypatch, resultado):
    async def _fake(*args, **kwargs):
        return resultado

    monkeypatch.setattr(perfil_module, "peticion_autenticada", _fake)


async def test_obtener_mis_empresas(monkeypatch):
    _mockear_peticion(
        monkeypatch,
        ApiExito(
            datos=[
                {
                    "empresaId": "e-1",
                    "razonSocial": "Ana S.A.",
                    "nombreComercial": "Ana",
                    "rolCodigo": "ADMIN_EMPRESA",
                    "estadoMembresia": "ACTIVO",
                }
            ]
        ),
    )

    resultado = await obtener_mis_empresas("token-seleccion")

    assert isinstance(resultado, ApiExito)
    assert resultado.datos == [
        EmpresaResumen(
            empresa_id="e-1",
            razon_social="Ana S.A.",
            nombre_comercial="Ana",
            rol_codigo="ADMIN_EMPRESA",
            estado_membresia="ACTIVO",
        )
    ]


async def test_obtener_mis_empresas_fallo(monkeypatch):
    _mockear_peticion(
        monkeypatch,
        ApiFallo(error=ErrorApi(mensaje="No autenticado.", status=401)),
    )

    resultado = await obtener_mis_empresas("token-invalido")

    assert isinstance(resultado, ApiFallo)


async def test_obtener_perfil(monkeypatch):
    _mockear_peticion_autenticada(
        monkeypatch,
        ApiExito(
            datos={
                "usuarioId": "u-1",
                "nombre": "Ana",
                "email": "ana@x.com",
                "mfaHabilitado": True,
                "empresaActiva": {
                    "empresaId": "e-1",
                    "razonSocial": "Ana S.A.",
                    "nombreComercial": "Ana",
                },
                "permisos": ["factura.crear"],
            }
        ),
    )

    resultado = await obtener_perfil()

    assert isinstance(resultado, ApiExito)
    assert isinstance(resultado.datos, PerfilUsuario)
    assert resultado.datos.nombre == "Ana"
    assert resultado.datos.empresa_activa.empresa_id == "e-1"
    assert resultado.datos.permisos == ["factura.crear"]
