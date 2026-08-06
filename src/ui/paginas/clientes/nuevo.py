import flet as ft

import rutas
from api.clientes import ClienteCreado, crear_cliente
from ui.componentes.shell_protegido import construir_vista_protegida
from ui.paginas.clientes.formulario import construir_formulario_cliente


def vista_clientes_nuevo(page: ft.Page) -> ft.View:
    def al_exito(cliente_creado: ClienteCreado) -> None:
        page.navigate(rutas.CLIENTES_DETALLE, id=cliente_creado.id)

    formulario = construir_formulario_cliente(
        page, None, crear_cliente, al_exito, texto_boton="Crear cliente"
    )

    contenido_pagina = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Nuevo cliente", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
                    ft.TextButton(
                        content="Volver a clientes",
                        on_click=lambda e: page.navigate(rutas.CLIENTES),
                    ),
                ],
            ),
            formulario,
        ],
    )

    return construir_vista_protegida(page, rutas.CLIENTES_NUEVO, rutas.CLIENTES, contenido_pagina)
