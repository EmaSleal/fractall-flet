from dataclasses import dataclass

import flet as ft

import router_query
import rutas
from api import sesion
from api.auth import cambiar_tenant
from api.cliente import ApiFallo
from api.cliente_autenticado import SesionExpirada
from api.cliente_autenticado import cerrar_sesion as cerrar_sesion_api
from api.perfil import PerfilUsuario, obtener_mis_empresas, obtener_perfil
from diseno import tokens
from ui.componentes.resize import registrar_oyente_resize

ANCHO_SIDEBAR = 224.0

_ITEMS_NAV = [
    (rutas.FACTURAS, "Facturas", ft.Icons.RECEIPT_LONG),
    (rutas.CLIENTES, "Clientes", ft.Icons.PEOPLE),
    (rutas.PRODUCTOS, "Productos", ft.Icons.INVENTORY_2),
    (rutas.EMPRESA, "Empresa", ft.Icons.BUSINESS),
]


def _es_movil(page: ft.Page) -> bool:
    return (page.width or tokens.ANCHO_PUNTO_QUIEBRE_MOVIL) < tokens.ANCHO_PUNTO_QUIEBRE_MOVIL


def _item_nav(
    page: ft.Page,
    ruta_activa: str,
    ruta: str,
    etiqueta: str,
    icono: str,
    cerrar_drawer: bool = False,
) -> ft.Container:
    activo = router_query.ruta_base(ruta_activa) == ruta
    color = tokens.COSECHA if activo else tokens.GRAFITO

    async def al_click(e: ft.Event[ft.Container]) -> None:
        if cerrar_drawer:
            await page.close_drawer()
        page.navigate(ruta)

    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=12, vertical=10),
        border_radius=tokens.RADIO_MD,
        bgcolor=ft.Colors.with_opacity(0.1, tokens.COSECHA) if activo else None,
        ink=True,
        on_click=al_click,
        content=ft.Row(
            spacing=12,
            controls=[
                ft.Icon(icono, size=18, color=color),
                ft.Text(etiqueta, theme_style=ft.TextThemeStyle.LABEL_LARGE, color=color),
            ],
        ),
    )


def _construir_items_nav(
    page: ft.Page, ruta_activa: str, cerrar_drawer: bool = False
) -> list[ft.Container]:
    return [
        _item_nav(page, ruta_activa, ruta, etiqueta, icono, cerrar_drawer)
        for ruta, etiqueta, icono in _ITEMS_NAV
    ]


def _construir_encabezado_marca() -> ft.Container:
    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=16, vertical=20),
        border=ft.Border(bottom=ft.BorderSide(1, tokens.ARENA)),
        content=ft.Text(
            "FRACTALL",
            theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
            font_family=tokens.FUENTE_DISPLAY_SEMIBOLD,
        ),
    )


def _construir_sidebar(page: ft.Page, ruta_activa: str, pie: ft.Control) -> ft.Container:
    return ft.Container(
        width=ANCHO_SIDEBAR,
        bgcolor=tokens.LINO,
        border=ft.Border(right=ft.BorderSide(1, tokens.ARENA)),
        content=ft.Column(
            controls=[
                _construir_encabezado_marca(),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=8, vertical=16),
                    content=ft.Column(
                        spacing=4, controls=_construir_items_nav(page, ruta_activa)
                    ),
                ),
                pie,
            ],
        ),
    )


def _construir_encabezado_drawer(page: ft.Page) -> ft.Container:
    async def al_cerrar(e: ft.Event[ft.IconButton]) -> None:
        await page.close_drawer()

    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        border=ft.Border(bottom=ft.BorderSide(1, tokens.ARENA)),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "FRACTALL",
                    theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                    font_family=tokens.FUENTE_DISPLAY_SEMIBOLD,
                ),
                ft.IconButton(icon=ft.Icons.CLOSE, tooltip="Cerrar menú", on_click=al_cerrar),
            ],
        ),
    )


def _construir_drawer(page: ft.Page, ruta_activa: str, pie: ft.Control) -> ft.NavigationDrawer:
    """Reemplaza al sidebar fijo en pantallas angostas (celular) — se abre
    desde el botón hamburguesa del topbar. El sidebar fijo del frontend
    (w-56, sin comportamiento responsive) no tiene equivalente móvil que
    portar; este drawer es diseño propio de fractall-flet."""
    return ft.NavigationDrawer(
        bgcolor=tokens.LINO,
        controls=[
            _construir_encabezado_drawer(page),
            ft.Container(
                padding=ft.Padding.symmetric(horizontal=8, vertical=16),
                content=ft.Column(
                    spacing=4,
                    controls=_construir_items_nav(page, ruta_activa, cerrar_drawer=True),
                ),
            ),
            pie,
        ],
    )


def _construir_selector_empresa(
    page: ft.Page,
    perfil: PerfilUsuario,
    empresas: list,
    cerrar_drawer: bool = False,
) -> ft.PopupMenuButton:
    """Selector de empresa activa, pineado al final del sidebar (y del
    drawer en celular) en vez de vivir en el topbar — con varias empresas
    listadas, el nombre completo compite por espacio con el menú de perfil
    ahí arriba."""
    empresa_activa = perfil.empresa_activa
    nombre_empresa_activa = empresa_activa.nombre_comercial or empresa_activa.razon_social

    async def al_cambiar_tenant(empresa_id: str) -> None:
        if cerrar_drawer:
            await page.close_drawer()
        if empresa_id == empresa_activa.empresa_id:
            return
        resultado = await cambiar_tenant(empresa_id)
        if isinstance(resultado, ApiFallo):
            return
        refresh_actual = await sesion.obtener_token_refresco()
        await sesion.guardar_tokens(resultado.datos.access_token, refresh_actual or "")
        await sesion.guardar_empresa_activa(resultado.datos.empresa_id)
        # recarga la vista actual para reflejar los datos de la nueva empresa
        page.navigate(page.route)

    return ft.PopupMenuButton(
        content=ft.Container(
            padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            border_radius=tokens.RADIO_MD,
            ink=True,
            content=ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.BUSINESS, size=18, color=tokens.GRAFITO),
                    ft.Text(
                        nombre_empresa_activa,
                        theme_style=ft.TextThemeStyle.LABEL_LARGE,
                        max_lines=1,
                        expand=True,
                    ),
                    ft.Icon(ft.Icons.UNFOLD_MORE, size=16, color=tokens.GRAFITO),
                ],
            ),
        ),
        items=[
            ft.PopupMenuItem(
                content=e.nombre_comercial or e.razon_social,
                on_click=lambda ev, eid=e.empresa_id: page.run_task(al_cambiar_tenant, eid),
            )
            for e in empresas
        ],
    )


def _construir_topbar(
    page: ft.Page,
    perfil: PerfilUsuario,
    boton_hamburguesa: ft.IconButton,
    movil: bool,
) -> ft.Container:
    """En celular, el sidebar se reemplaza por un botón hamburguesa que ya
    ocupa espacio en el topbar — mostrar además el nombre del usuario en
    texto completo lo hace ver amontonado en una pantalla angosta, así que
    en `movil` el menú de perfil se reduce a solo su ícono (sigue abriendo
    el mismo menú, solo sin la etiqueta de texto)."""

    async def al_cerrar_sesion(e: ft.Event[ft.PopupMenuItem]) -> None:
        await cerrar_sesion_api()
        page.navigate(rutas.LOGIN)

    contenido_perfil: ft.Control = (
        ft.Icon(ft.Icons.PERSON, size=20, color=tokens.GRAFITO)
        if movil
        else ft.Row(
            spacing=6,
            tight=True,
            controls=[
                ft.Icon(ft.Icons.PERSON, size=16, color=tokens.GRAFITO),
                ft.Text(perfil.nombre, theme_style=ft.TextThemeStyle.LABEL_LARGE, max_lines=1),
                ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=16, color=tokens.GRAFITO),
            ],
        )
    )

    menu_perfil = ft.PopupMenuButton(
        content=contenido_perfil,
        tooltip=perfil.nombre if movil else None,
        items=[
            ft.PopupMenuItem(content=f"{perfil.nombre} · {perfil.email}"),
            ft.PopupMenuItem(
                content="Mi perfil",
                icon=ft.Icons.PERSON_OUTLINE,
                on_click=lambda e: page.navigate(rutas.PERFIL),
            ),
            ft.PopupMenuItem(
                content="Cerrar sesión",
                icon=ft.Icons.LOGOUT,
                on_click=al_cerrar_sesion,
            ),
        ],
    )

    return ft.Container(
        height=56,
        bgcolor=tokens.LINO,
        border=ft.Border(bottom=ft.BorderSide(1, tokens.ARENA)),
        padding=ft.Padding.symmetric(horizontal=24),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[boton_hamburguesa, menu_perfil],
        ),
    )


def _construir_pie_selector() -> ft.Container:
    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=8, vertical=12),
        border=ft.Border(top=ft.BorderSide(1, tokens.ARENA)),
    )


@dataclass
class _Shell:
    contenido: ft.Control
    drawer: ft.NavigationDrawer


def _construir_shell(page: ft.Page, ruta_activa: str, contenido_pagina: ft.Control) -> _Shell:
    """Arma sidebar + topbar + contenido + drawer. A diferencia del frontend
    (que carga perfil/empresas una sola vez en el layout server-side y las
    comparte vía Context), acá el shell hace su propia carga liviana en
    cada navegación — Flet no tiene un layout persistente entre cambios de
    ruta con el router actual (una vista completa se reemplaza por otra en
    cada navegación).

    El contenido de la página no lleva un ancho máximo propio: igual que
    `app/(app)/layout.tsx` en el frontend (`<main className="flex-1 p-6">`,
    sin max-width), se deja que ocupe todo el espacio disponible junto al
    sidebar."""
    pie_sidebar = _construir_pie_selector()
    pie_drawer = _construir_pie_selector()
    sidebar = _construir_sidebar(page, ruta_activa, pie_sidebar)
    drawer = _construir_drawer(page, ruta_activa, pie_drawer)
    boton_hamburguesa = ft.IconButton(
        icon=ft.Icons.MENU,
        tooltip="Menú",
        on_click=lambda e: page.run_task(page.show_drawer),
    )
    contenedor_topbar = ft.Container(height=56, bgcolor=tokens.LINO)
    datos_cuenta: dict = {"perfil": None, "empresas": None}

    def refrescar_cuenta() -> None:
        # se llama tanto al terminar de cargar perfil/empresas como en cada
        # resize, para que el topbar pase de texto completo a solo-ícono
        # (o viceversa) si el resize cruza el punto de quiebre móvil.
        if datos_cuenta["perfil"] is None:
            return
        perfil = datos_cuenta["perfil"]
        empresas = datos_cuenta["empresas"]

        nuevo_topbar = _construir_topbar(page, perfil, boton_hamburguesa, _es_movil(page))
        contenedor_topbar.content = nuevo_topbar.content
        contenedor_topbar.padding = nuevo_topbar.padding

        pie_sidebar.content = _construir_selector_empresa(page, perfil, empresas)
        pie_drawer.content = _construir_selector_empresa(
            page, perfil, empresas, cerrar_drawer=True
        )

    def ajustar_layout(e: ft.PageResizeEvent | None = None) -> None:
        movil = _es_movil(page)
        sidebar.visible = not movil
        boton_hamburguesa.visible = movil
        refrescar_cuenta()
        if e is not None:
            page.update()

    ajustar_layout()
    registrar_oyente_resize(page, ajustar_layout)

    async def cargar_cuenta() -> None:
        try:
            resultado_perfil = await obtener_perfil()
        except SesionExpirada:
            page.navigate(rutas.LOGIN)
            return
        if isinstance(resultado_perfil, ApiFallo):
            return

        token = await sesion.obtener_token_acceso()
        empresas = []
        if token:
            resultado_empresas = await obtener_mis_empresas(token)
            if not isinstance(resultado_empresas, ApiFallo):
                empresas = resultado_empresas.datos

        datos_cuenta["perfil"] = resultado_perfil.datos
        datos_cuenta["empresas"] = empresas
        refrescar_cuenta()
        page.update()

    page.run_task(cargar_cuenta)

    contenido = ft.Row(
        expand=True,
        spacing=0,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            sidebar,
            ft.Column(
                expand=True,
                spacing=0,
                controls=[
                    contenedor_topbar,
                    ft.Container(
                        expand=True,
                        padding=24,
                        content=ft.Column(
                            scroll=ft.ScrollMode.AUTO,
                            expand=True,
                            controls=[contenido_pagina],
                        ),
                    ),
                ],
            ),
        ],
    )
    return _Shell(contenido=contenido, drawer=drawer)


def construir_vista_protegida(
    page: ft.Page,
    route: str,
    ruta_activa: str,
    contenido_pagina: ft.Control,
) -> ft.View:
    """Arma la `View` completa de una página protegida (sidebar + topbar +
    contenido + drawer de navegación para celular). El drawer se define acá,
    a nivel de `View`, porque `ft.View.drawer` solo tiene efecto si se pasa
    en la construcción de la vista — no se puede "inyectar" desde un control
    hijo después."""
    shell = _construir_shell(page, ruta_activa, contenido_pagina)
    return ft.View(
        route=route,
        drawer=shell.drawer,
        controls=[ft.SafeArea(expand=True, content=shell.contenido)],
    )
