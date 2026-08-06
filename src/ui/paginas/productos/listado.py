import flet as ft

import formato
import rutas
from api.productos import Producto, listar_productos
from diseno import tokens
from ui.componentes.paginacion import calcular_limite_pagina, construir_lista_paginada
from ui.componentes.shell_protegido import construir_vista_protegida


def _fila_producto(producto: Producto, page: ft.Page) -> ft.Container:
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
                        ft.Text(
                            producto.descripcion, theme_style=ft.TextThemeStyle.TITLE_MEDIUM
                        ),
                        ft.Text(
                            f"{producto.codigo} · CABYS {producto.codigo_cabys or '—'}",
                            theme_style=ft.TextThemeStyle.BODY_SMALL,
                            color=tokens.GRAFITO,
                        ),
                        ft.Text(
                            f"{formato.formatear_moneda(producto.precio_venta)} · "
                            f"IVA {producto.porcentaje_impuesto}%",
                            theme_style=ft.TextThemeStyle.BODY_SMALL,
                            font_family=tokens.FUENTE_MONO,
                            color=tokens.GRAFITO,
                        ),
                    ],
                ),
                ft.TextButton(
                    content="Ver detalle",
                    on_click=lambda e: page.navigate(
                        rutas.PRODUCTOS_DETALLE, id=producto.id
                    ),
                ),
            ],
        ),
    )


def vista_productos(page: ft.Page) -> ft.View:
    limite_pagina = calcular_limite_pagina(page)

    texto_vacio = ft.Column(
        visible=False,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=8,
        controls=[
            ft.Text(
                "Aún no tiene productos registrados",
                theme_style=ft.TextThemeStyle.BODY_MEDIUM,
            ),
            ft.Button(
                content="Agregar el primero",
                on_click=lambda e: page.navigate(rutas.PRODUCTOS_NUEVO),
            ),
        ],
    )

    interruptor_activos = ft.RadioGroup(
        value="true",
        content=ft.Row(
            controls=[
                ft.Radio(value="true", label="Activos"),
                ft.Radio(value="false", label="Inactivos"),
            ]
        ),
    )

    async def buscar(cursor: str | None):
        return await listar_productos(
            activo=interruptor_activos.value == "true",
            cursor=cursor,
            limit=limite_pagina,
        )

    lista = construir_lista_paginada(
        page,
        buscar=buscar,
        renderizar_fila=lambda producto: _fila_producto(producto, page),
        control_vacio=texto_vacio,
    )

    interruptor_activos.on_change = lista.recargar_desde_cero

    contenido_pagina = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Productos", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
                    ft.Button(
                        content="+ Nuevo",
                        on_click=lambda e: page.navigate(rutas.PRODUCTOS_NUEVO),
                    ),
                ],
            ),
            interruptor_activos,
            lista.contenido,
        ],
    )

    return construir_vista_protegida(page, rutas.PRODUCTOS, rutas.PRODUCTOS, contenido_pagina)
