from dataclasses import dataclass
from typing import Callable

import flet as ft
from flet_secure_storage import SecureStorage

import router_query
import rutas
from api import sesion
from diseno import tema, tokens
from ui.paginas.clientes.detalle import vista_clientes_detalle
from ui.paginas.clientes.exoneraciones import vista_clientes_exoneraciones
from ui.paginas.clientes.listado import vista_clientes
from ui.paginas.clientes.nuevo import vista_clientes_nuevo
from ui.paginas.dashboard import vista_dashboard
from ui.paginas.empresa import vista_empresa
from ui.paginas.facturas.detalle import vista_facturas_detalle
from ui.paginas.facturas.listado import vista_facturas
from ui.paginas.facturas.nota_credito.nueva.wizard import vista_facturas_nota_credito_nueva
from ui.paginas.facturas.nota_debito.nueva.wizard import vista_facturas_nota_debito_nueva
from ui.paginas.facturas.nueva.wizard import vista_facturas_nueva
from ui.paginas.facturas.tiquetes.nueva.wizard import vista_facturas_tiquetes_nueva
from ui.paginas.landing import vista_landing
from ui.paginas.login import vista_login
from ui.paginas.mfa_enrolar import vista_mfa_enrolar
from ui.paginas.mfa_verificar import vista_mfa_verificar
from ui.paginas.pendiente import vista_pendiente
from ui.paginas.perfil import vista_perfil
from ui.paginas.productos.detalle import vista_productos_detalle
from ui.paginas.productos.listado import vista_productos
from ui.paginas.productos.nuevo import vista_productos_nuevo
from ui.paginas.recuperar_password import vista_recuperar_password
from ui.paginas.registro import vista_registro
from ui.paginas.restablecer_password import vista_restablecer_password
from ui.paginas.seleccionar_tenant import vista_seleccionar_tenant
from ui.paginas.verificar_email import vista_verificar_email


@dataclass(frozen=True)
class _Ruta:
    vista: Callable[[ft.Page], ft.View]
    # Cada ruta declara acá mismo si es pública — antes esto vivía en un set
    # aparte (_RUTAS_PUBLICAS), separado de la tabla de despacho, con el
    # riesgo de agregar una ruta nueva y olvidarse de clasificarla en el
    # otro lado. Declarar los dos datos juntos elimina ese riesgo.
    publica: bool = False


# Tabla ruta → vista. Agregar una ruta nueva es una sola línea acá, en vez
# de un `if` más en construir_vista() — y no requiere tocar ningún otro
# lugar para que quede clasificada como pública o protegida.
_RUTAS: dict[str, _Ruta] = {
    rutas.LANDING: _Ruta(vista_landing, publica=True),
    rutas.LOGIN: _Ruta(vista_login, publica=True),
    rutas.REGISTRO: _Ruta(vista_registro, publica=True),
    rutas.SELECCIONAR_TENANT: _Ruta(vista_seleccionar_tenant, publica=True),
    rutas.MFA_VERIFICAR: _Ruta(vista_mfa_verificar, publica=True),
    rutas.MFA_ENROLAR: _Ruta(vista_mfa_enrolar, publica=True),
    rutas.DASHBOARD: _Ruta(vista_dashboard),
    rutas.RECUPERAR_PASSWORD: _Ruta(vista_recuperar_password, publica=True),
    rutas.RESTABLECER_PASSWORD: _Ruta(vista_restablecer_password, publica=True),
    rutas.VERIFICAR_EMAIL: _Ruta(vista_verificar_email, publica=True),
    rutas.PERFIL: _Ruta(vista_perfil),
    rutas.CLIENTES: _Ruta(vista_clientes),
    rutas.CLIENTES_NUEVO: _Ruta(vista_clientes_nuevo),
    rutas.CLIENTES_DETALLE: _Ruta(vista_clientes_detalle),
    rutas.CLIENTES_EXONERACIONES: _Ruta(vista_clientes_exoneraciones),
    rutas.EMPRESA: _Ruta(vista_empresa),
    rutas.PRODUCTOS: _Ruta(vista_productos),
    rutas.PRODUCTOS_NUEVO: _Ruta(vista_productos_nuevo),
    rutas.PRODUCTOS_DETALLE: _Ruta(vista_productos_detalle),
    rutas.FACTURAS: _Ruta(vista_facturas),
    rutas.FACTURAS_DETALLE: _Ruta(vista_facturas_detalle),
    rutas.FACTURAS_NUEVA: _Ruta(vista_facturas_nueva),
    rutas.FACTURAS_TIQUETES_NUEVA: _Ruta(vista_facturas_tiquetes_nueva),
    rutas.FACTURAS_NOTA_DEBITO_NUEVA: _Ruta(vista_facturas_nota_debito_nueva),
    rutas.FACTURAS_NOTA_CREDITO_NUEVA: _Ruta(vista_facturas_nota_credito_nueva),
}


async def main(page: ft.Page):
    page.title = "Fractall"
    tema.registrar_fuentes(page)
    page.theme = tema.construir_tema()
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = tokens.PAPEL

    almacen_seguro = SecureStorage()
    page.services.append(almacen_seguro)
    sesion.inicializar(page, almacen_seguro)

    def construir_vista(ruta: str) -> ft.View:
        base = router_query.ruta_base(ruta)
        entrada = _RUTAS.get(base)
        if entrada is None:
            return vista_pendiente(ruta)
        return entrada.vista(page)

    def al_cambiar_ruta(e: ft.RouteChangeEvent) -> None:
        page.views.clear()
        page.views.append(construir_vista(page.route))
        page.update()

    page.on_route_change = al_cambiar_ruta

    # Al conectar (primera carga o recarga del navegador), Flet ya trae
    # page.route sincronizado con la URL actual del navegador — si acá
    # forzáramos siempre rutas.LOGIN (como se hacía antes), cada recarga
    # descartaría tanto la ruta real como cualquier sesión guardada, aunque
    # el usuario ya estuviera logueado. Solo se decide algo en dos casos:
    # la raíz "/" (el landing público, igual que app/page.tsx en el
    # frontend: con sesión manda directo al dashboard, sin sesión se deja
    # tal cual) y cualquier otra ruta protegida sin sesión (manda a login).
    ruta_actual = router_query.ruta_base(page.route)
    if ruta_actual in ("", rutas.LANDING):
        if await sesion.hay_sesion_activa():
            page.route = rutas.DASHBOARD
    else:
        entrada = _RUTAS.get(ruta_actual)
        es_publica = entrada.publica if entrada else False
        if not es_publica and not await sesion.hay_sesion_activa():
            page.route = rutas.LOGIN

    page.views.append(construir_vista(page.route))


if __name__ == "__main__":
    ft.run(main)
