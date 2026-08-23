import flet as ft

import rutas
from diseno import tokens
from estado_tiquete import EstadoTiquete
from ui.componentes.shell_protegido import construir_vista_protegida
from ui.paginas.facturas.tiquetes.nueva.paso1_cliente import construir_paso1
from ui.paginas.facturas.tiquetes.nueva.paso2_lineas import construir_paso2
from ui.paginas.facturas.tiquetes.nueva.paso3_confirmacion import construir_paso3

_NOMBRES_PASO = {
    1: "Cliente",
    2: "Líneas",
    3: "Confirmación",
}


def vista_facturas_tiquetes_nueva(page: ft.Page) -> ft.View:
    estado = EstadoTiquete()

    indicador_paso = ft.Text(theme_style=ft.TextThemeStyle.BODY_SMALL, color=tokens.GRAFITO)
    contenedor_paso = ft.Column()

    def ir_a_paso(numero: int) -> None:
        estado.paso = numero
        renderizar()

    def renderizar() -> None:
        indicador_paso.value = f"Paso {estado.paso} de 3 — {_NOMBRES_PASO[estado.paso]}"
        if estado.paso == 1:
            contenedor_paso.controls = [construir_paso1(page, estado, ir_a_paso)]
        elif estado.paso == 2:
            contenedor_paso.controls = [construir_paso2(page, estado, ir_a_paso)]
        else:
            contenedor_paso.controls = [construir_paso3(page, estado, ir_a_paso)]
        page.update()

    renderizar()

    contenido_pagina = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Nuevo tiquete", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
                    ft.TextButton(
                        content="Cancelar",
                        on_click=lambda e: page.navigate(rutas.FACTURAS),
                    ),
                ],
            ),
            indicador_paso,
            contenedor_paso,
        ],
    )

    return construir_vista_protegida(
        page, rutas.FACTURAS_TIQUETES_NUEVA, rutas.FACTURAS, contenido_pagina
    )
