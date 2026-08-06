import flet as ft

import rutas
from api.clientes import Cliente, listar_clientes
from catalogos import label_tipo_identificacion
from diseno import tokens
from ui.componentes.paginacion import calcular_limite_pagina, construir_lista_paginada
from ui.componentes.shell_protegido import construir_vista_protegida


def _fila_cliente(cliente: Cliente, page: ft.Page) -> ft.Container:
    return ft.Container(
        border=ft.Border.all(1, tokens.ARENA),
        border_radius=tokens.RADIO_LG,
        bgcolor=tokens.LINO,
        padding=16,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=2,
                    expand=True,
                    controls=[
                        ft.Text(cliente.nombre, theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                        ft.Text(
                            f"{label_tipo_identificacion(cliente.tipo_identificacion)} · "
                            f"{cliente.numero_identificacion}",
                            theme_style=ft.TextThemeStyle.BODY_SMALL,
                            color=tokens.GRAFITO,
                        ),
                        ft.Text(
                            cliente.telefono or cliente.email or "",
                            theme_style=ft.TextThemeStyle.BODY_SMALL,
                            color=tokens.GRAFITO,
                        ),
                    ],
                ),
                ft.TextButton(
                    content="Ver detalle",
                    on_click=lambda e: page.navigate(
                        rutas.CLIENTES_DETALLE, id=cliente.id
                    ),
                ),
            ],
        ),
    )


def vista_clientes(page: ft.Page) -> ft.View:
    limite_pagina = calcular_limite_pagina(page)

    campo_busqueda = ft.TextField(
        label="Buscar por nombre o identificación",
        prefix_icon=ft.Icons.SEARCH,
    )
    texto_vacio = ft.Column(
        visible=False,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=8,
        controls=[
            ft.Text("Aún no tiene clientes registrados", theme_style=ft.TextThemeStyle.BODY_MEDIUM),
            ft.Button(
                content="Agregar el primero",
                on_click=lambda e: page.navigate(rutas.CLIENTES_NUEVO),
            ),
        ],
    )

    async def buscar(cursor: str | None):
        return await listar_clientes(
            q=campo_busqueda.value.strip(), cursor=cursor, limit=limite_pagina
        )

    lista = construir_lista_paginada(
        page,
        buscar=buscar,
        renderizar_fila=lambda cliente: _fila_cliente(cliente, page),
        control_vacio=texto_vacio,
    )

    campo_busqueda.on_submit = lista.recargar_desde_cero

    contenido_pagina = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Clientes", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
                    ft.Button(
                        content="+ Nuevo",
                        on_click=lambda e: page.navigate(rutas.CLIENTES_NUEVO),
                    ),
                ],
            ),
            ft.Row(
                controls=[
                    ft.Container(expand=True, content=campo_busqueda),
                    ft.IconButton(icon=ft.Icons.SEARCH, on_click=lista.recargar_desde_cero),
                ],
            ),
            lista.contenido,
        ],
    )

    return construir_vista_protegida(page, rutas.CLIENTES, rutas.CLIENTES, contenido_pagina)
