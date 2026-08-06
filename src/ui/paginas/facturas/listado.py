from datetime import datetime

import flet as ft

import catalogos
import formato
import rutas
from api.facturas import FacturaResumen, listar_facturas
from diseno import tokens
from ui.componentes.paginacion import calcular_limite_pagina, construir_lista_paginada
from ui.componentes.sello_estado import construir_sello_estado
from ui.componentes.shell_protegido import construir_vista_protegida


def _fila_factura(factura: FacturaResumen, page: ft.Page) -> ft.Container:
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
                            factura.consecutivo,
                            theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                            font_family=tokens.FUENTE_MONO,
                        ),
                        ft.Text(
                            factura.cliente_nombre,
                            theme_style=ft.TextThemeStyle.BODY_SMALL,
                            color=tokens.GRAFITO,
                        ),
                        ft.Text(
                            f"{formato.formatear_moneda(factura.total, factura.moneda)} · "
                            f"{formato.formatear_fecha(factura.fecha_emision)}",
                            theme_style=ft.TextThemeStyle.BODY_SMALL,
                            font_family=tokens.FUENTE_MONO,
                            color=tokens.GRAFITO,
                        ),
                    ],
                ),
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                    controls=[
                        construir_sello_estado(factura.estado),
                        ft.TextButton(
                            content="Ver detalle",
                            on_click=lambda e: page.navigate(
                                rutas.FACTURAS_DETALLE, id=factura.id
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )


def vista_facturas(page: ft.Page) -> ft.View:
    limite_pagina = calcular_limite_pagina(page)

    campo_estado = ft.Dropdown(
        label="Estado",
        value="",
        options=[ft.DropdownOption(key="", text="Todos los estados")]
        + [
            ft.DropdownOption(key=clave, text=etiqueta)
            for clave, (etiqueta, _icono, _cat) in catalogos.ESTADOS_FACTURA.items()
        ],
    )

    estado_fechas = {"desde": None, "hasta": None}
    texto_desde = ft.Text("Desde: sin definir", theme_style=ft.TextThemeStyle.BODY_SMALL)
    texto_hasta = ft.Text("Hasta: sin definir", theme_style=ft.TextThemeStyle.BODY_SMALL)

    async def al_elegir_desde(e: ft.Event[ft.DatePicker]) -> None:
        if picker_desde.value:
            estado_fechas["desde"] = picker_desde.value
            texto_desde.value = f"Desde: {picker_desde.value.strftime('%d/%m/%Y')}"
            page.update()

    async def al_elegir_hasta(e: ft.Event[ft.DatePicker]) -> None:
        if picker_hasta.value:
            estado_fechas["hasta"] = picker_hasta.value
            texto_hasta.value = f"Hasta: {picker_hasta.value.strftime('%d/%m/%Y')}"
            page.update()

    picker_desde = ft.DatePicker(
        first_date=datetime(2000, 1, 1), last_date=datetime(2100, 1, 1), on_change=al_elegir_desde
    )
    picker_hasta = ft.DatePicker(
        first_date=datetime(2000, 1, 1), last_date=datetime(2100, 1, 1), on_change=al_elegir_hasta
    )

    texto_vacio = ft.Text(
        "Aún no tiene facturas emitidas", theme_style=ft.TextThemeStyle.BODY_MEDIUM, visible=False
    )

    async def buscar(cursor: str | None):
        return await listar_facturas(
            estado=campo_estado.value or "",
            desde=formato.fecha_a_iso(estado_fechas["desde"]) if estado_fechas["desde"] else "",
            hasta=formato.fecha_a_iso(estado_fechas["hasta"]) if estado_fechas["hasta"] else "",
            cursor=cursor,
            limit=limite_pagina,
        )

    lista = construir_lista_paginada(
        page,
        buscar=buscar,
        renderizar_fila=lambda factura: _fila_factura(factura, page),
        control_vacio=texto_vacio,
    )

    campo_estado.on_select = lista.recargar_desde_cero

    boton_aplicar_fechas = ft.TextButton(
        content="Aplicar filtro de fechas",
        on_click=lambda e: page.run_task(lista.recargar_desde_cero),
    )

    contenido_pagina = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Facturas", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
                    ft.Button(
                        content="+ Nueva factura",
                        on_click=lambda e: page.navigate(rutas.FACTURAS_NUEVA),
                    ),
                ],
            ),
            campo_estado,
            ft.Row(
                controls=[
                    texto_desde,
                    ft.IconButton(
                        icon=ft.Icons.CALENDAR_MONTH,
                        on_click=lambda e: page.show_dialog(picker_desde),
                    ),
                    texto_hasta,
                    ft.IconButton(
                        icon=ft.Icons.CALENDAR_MONTH,
                        on_click=lambda e: page.show_dialog(picker_hasta),
                    ),
                    boton_aplicar_fechas,
                ]
            ),
            lista.contenido,
        ],
    )

    return construir_vista_protegida(page, rutas.FACTURAS, rutas.FACTURAS, contenido_pagina)
