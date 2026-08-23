from typing import Callable

import flet as ft

import validacion_tiquete
from diseno import tokens
from estado_tiquete import EstadoTiquete
from ui.paginas.facturas.nueva.paso2_lineas import construir_fila_linea


def construir_paso2(
    page: ft.Page, estado: EstadoTiquete, ir_a_paso: Callable[[int], None]
) -> ft.Column:
    contenedor_lineas = ft.Column(spacing=12)
    texto_error = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    boton_anterior = ft.TextButton(content="Anterior")
    boton_siguiente = ft.Button(content="Siguiente")
    boton_agregar = ft.TextButton(content="+ Agregar línea")

    def al_eliminar_linea(indice: int) -> None:
        estado.quitar_linea(indice)
        renderizar_lineas()

    def renderizar_lineas() -> None:
        contenedor_lineas.controls = [
            construir_fila_linea(
                page,
                estado,
                linea,
                al_eliminar=lambda i=i: al_eliminar_linea(i),
                es_unica=len(estado.lineas) <= 1,
            )
            for i, linea in enumerate(estado.lineas)
        ]
        page.update()

    def al_agregar_linea(e: ft.Event[ft.TextButton]) -> None:
        estado.agregar_linea()
        renderizar_lineas()

    boton_agregar.on_click = al_agregar_linea

    def al_anterior(e: ft.Event[ft.TextButton]) -> None:
        ir_a_paso(1)

    def al_siguiente(e: ft.Event[ft.Button]) -> None:
        errores = validacion_tiquete.validar_paso2(estado)
        if errores:
            texto_error.value = "Revisá las líneas: falta elegir producto, o cantidad/precio inválidos."
            texto_error.visible = True
            page.update()
            return
        texto_error.visible = False
        ir_a_paso(3)

    boton_anterior.on_click = al_anterior
    boton_siguiente.on_click = al_siguiente

    renderizar_lineas()

    return ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        controls=[
            ft.Text("Paso 2 — Líneas", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            contenedor_lineas,
            boton_agregar,
            texto_error,
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[boton_anterior, boton_siguiente],
            ),
        ],
    )
