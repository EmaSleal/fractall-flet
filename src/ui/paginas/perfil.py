import flet as ft

import rutas
from api.cliente import ApiFallo
from api.cliente_autenticado import SesionExpirada
from api.perfil import obtener_perfil
from diseno import tokens
from ui.componentes.shell_protegido import construir_vista_protegida


def _fila_dato(etiqueta: str, valor: str) -> ft.Column:
    return ft.Column(
        spacing=2,
        controls=[
            ft.Text(
                etiqueta.upper(),
                theme_style=ft.TextThemeStyle.LABEL_MEDIUM,
                color=tokens.GRAFITO,
            ),
            ft.Text(valor, theme_style=ft.TextThemeStyle.BODY_LARGE),
        ],
    )


def vista_perfil(page: ft.Page) -> ft.View:
    texto_estado = ft.Text("Cargando...", theme_style=ft.TextThemeStyle.BODY_SMALL)
    contenido = ft.Column(visible=False, spacing=20)

    async def cargar() -> None:
        try:
            resultado = await obtener_perfil()
        except SesionExpirada:
            page.navigate(rutas.LOGIN)
            return

        if isinstance(resultado, ApiFallo):
            page.navigate(rutas.LOGIN)
            return

        perfil = resultado.datos
        empresa = perfil.empresa_activa

        texto_estado.visible = False
        contenido.controls = [
            _fila_dato("Nombre", perfil.nombre),
            _fila_dato("Correo electrónico", perfil.email),
            _fila_dato(
                "Empresa activa", empresa.nombre_comercial or empresa.razon_social
            ),
            _fila_dato(
                "Verificación en dos pasos (MFA)",
                "Activa" if perfil.mfa_habilitado else "Inactiva",
            ),
            ft.Divider(),
            ft.TextButton(
                content="Cambiar contraseña",
                on_click=lambda e: page.navigate(rutas.RECUPERAR_PASSWORD),
            ),
        ]
        contenido.visible = True
        page.update()

    page.run_task(cargar)

    contenido_pagina = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        controls=[
            ft.Text("Mi perfil", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
            texto_estado,
            contenido,
        ],
    )

    return construir_vista_protegida(page, rutas.PERFIL, rutas.PERFIL, contenido_pagina)
