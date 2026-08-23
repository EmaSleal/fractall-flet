from typing import Callable

import flet as ft

import catalogos
import validacion_nota_credito
from diseno import tokens
from estado_nota_credito import EstadoNotaCredito


def construir_paso1(
    page: ft.Page, estado: EstadoNotaCredito, ir_a_paso: Callable[[int], None]
) -> ft.Column:
    campo_codigo_referencia = ft.Dropdown(
        label="Código de referencia",
        value=estado.codigo_referencia or None,
        options=[
            ft.DropdownOption(key=clave, text=f"{clave} — {etiqueta}")
            for clave, etiqueta in catalogos.CODIGOS_REFERENCIA
        ],
    )
    campo_codigo_referencia_otro = ft.TextField(
        label="Descripción del motivo",
        value=estado.codigo_referencia_otro,
        visible=estado.codigo_referencia == "99",
    )
    campo_razon = ft.TextField(
        label="Razón (opcional)",
        value=estado.razon,
        max_length=180,
        multiline=True,
        max_lines=3,
    )

    def al_cambiar_codigo_referencia(e: ft.Event[ft.Dropdown]) -> None:
        estado.establecer_codigo_referencia(campo_codigo_referencia.value or "")
        campo_codigo_referencia.error_text = None
        campo_codigo_referencia_otro.visible = estado.codigo_referencia == "99"
        campo_codigo_referencia_otro.value = estado.codigo_referencia_otro
        page.update()

    campo_codigo_referencia.on_select = al_cambiar_codigo_referencia

    texto_error = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    boton_siguiente = ft.Button(content="Siguiente")

    def limpiar_errores() -> None:
        campo_codigo_referencia.error_text = None
        campo_codigo_referencia_otro.error = None
        campo_razon.error = None
        texto_error.visible = False

    def al_siguiente(e: ft.Event[ft.Button]) -> None:
        limpiar_errores()
        estado.codigo_referencia_otro = campo_codigo_referencia_otro.value
        estado.razon = campo_razon.value

        errores = validacion_nota_credito.validar_paso1(estado)
        if errores:
            mapa = {
                "codigo_referencia_otro": campo_codigo_referencia_otro,
                "razon": campo_razon,
            }
            for clave, mensaje in errores.items():
                if clave == "codigo_referencia":
                    campo_codigo_referencia.error_text = mensaje
                elif clave in mapa:
                    mapa[clave].error = mensaje
            page.update()
            return

        ir_a_paso(2)

    boton_siguiente.on_click = al_siguiente
    campo_codigo_referencia_otro.on_submit = al_siguiente
    campo_razon.on_submit = al_siguiente

    return ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        controls=[
            ft.Text("Paso 1 — Motivo", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            ft.Text(
                f"Corrige a: {estado.factura_origen_consecutivo}",
                theme_style=ft.TextThemeStyle.BODY_SMALL,
                color=tokens.GRAFITO,
                font_family=tokens.FUENTE_MONO,
            ),
            ft.Text(
                f"Cliente: {estado.cliente_nombre}",
                theme_style=ft.TextThemeStyle.BODY_SMALL,
                color=tokens.GRAFITO,
            ),
            campo_codigo_referencia,
            campo_codigo_referencia_otro,
            campo_razon,
            texto_error,
            ft.Row(alignment=ft.MainAxisAlignment.END, controls=[boton_siguiente]),
        ],
    )
