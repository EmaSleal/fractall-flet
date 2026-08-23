"""Paso 2 del wizard de Nota de Crédito — a diferencia de Factura/Tiquete/ND,
acá NO se arman líneas nuevas desde el catálogo de productos: se muestran
TODAS las líneas de la factura origen, precargadas y de solo-mostrar-datos
(sin selector de producto), cada una con un checkbox de selección y una
cantidad a acreditar editable. Los totales del pie son una estimación
proporcional (ver estado_nota_credito.calcular_*_acreditar) — el backend es
la fuente de verdad final."""

from typing import Callable

import flet as ft

import formato
import validacion_nota_credito
from diseno import tokens
from estado_nota_credito import (
    EstadoNotaCredito,
    LineaNcSeleccionable,
    calcular_iva_total_acreditar,
    calcular_subtotal_acreditar,
    calcular_subtotal_total_acreditar,
    calcular_total_acreditar,
)


def _construir_fila_linea_nc(
    page: ft.Page,
    estado: EstadoNotaCredito,
    linea: LineaNcSeleccionable,
    indice: int,
    al_cambiar: Callable[[], None],
) -> ft.Container:
    campo_cantidad = ft.TextField(
        label="Cantidad a acreditar",
        keyboard_type=ft.KeyboardType.NUMBER,
        value=str(linea.cantidad_acreditar),
        disabled=not linea.seleccionada,
        width=180,
    )
    texto_subtotal_acreditar = ft.Text(
        theme_style=ft.TextThemeStyle.BODY_SMALL, color=tokens.GRAFITO
    )

    def refrescar_subtotal() -> None:
        if linea.seleccionada:
            subtotal = calcular_subtotal_acreditar(linea)
            texto_subtotal_acreditar.value = (
                f"Subtotal a acreditar: {formato.formatear_moneda(subtotal, estado.moneda)}"
            )
        else:
            texto_subtotal_acreditar.value = "No incluida en la nota de crédito"

    def al_cambiar_seleccion(e: ft.Event[ft.Checkbox]) -> None:
        estado.alternar_seleccion_linea(indice)
        campo_cantidad.disabled = not linea.seleccionada
        refrescar_subtotal()
        al_cambiar()
        page.update()

    def al_cambiar_cantidad(e: ft.Event[ft.TextField]) -> None:
        try:
            valor = float(campo_cantidad.value)
        except (TypeError, ValueError):
            valor = 0.0
        estado.establecer_cantidad_acreditar(indice, valor)
        refrescar_subtotal()
        al_cambiar()
        page.update()

    checkbox = ft.Checkbox(
        value=linea.seleccionada,
        label=(
            f"#{linea.numero_linea} · CABYS {linea.codigo_cabys_aplicado or '—'} · "
            f"{linea.cantidad_origen} {linea.unidad_medida_comercial or ''} × "
            f"{formato.formatear_moneda(linea.precio_unitario, estado.moneda)} = "
            f"{formato.formatear_moneda(linea.subtotal_origen, estado.moneda)}"
        ),
    )
    checkbox.on_change = al_cambiar_seleccion
    campo_cantidad.on_change = al_cambiar_cantidad

    refrescar_subtotal()

    return ft.Container(
        border=ft.Border.all(1, tokens.ARENA),
        border_radius=tokens.RADIO_LG,
        padding=16,
        content=ft.Column(
            spacing=8,
            controls=[checkbox, campo_cantidad, texto_subtotal_acreditar],
        ),
    )


def construir_paso2(
    page: ft.Page, estado: EstadoNotaCredito, ir_a_paso: Callable[[int], None]
) -> ft.Column:
    texto_error = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    texto_subtotal = ft.Text(
        theme_style=ft.TextThemeStyle.BODY_MEDIUM, font_family=tokens.FUENTE_MONO
    )
    texto_iva = ft.Text(
        theme_style=ft.TextThemeStyle.BODY_MEDIUM, font_family=tokens.FUENTE_MONO
    )
    texto_total = ft.Text(
        theme_style=ft.TextThemeStyle.TITLE_MEDIUM, font_family=tokens.FUENTE_MONO
    )

    def actualizar_totales() -> None:
        texto_subtotal.value = (
            f"Subtotal a acreditar: "
            f"{formato.formatear_moneda(calcular_subtotal_total_acreditar(estado.lineas), estado.moneda)}"
        )
        texto_iva.value = (
            f"IVA (estimado): "
            f"{formato.formatear_moneda(calcular_iva_total_acreditar(estado.lineas), estado.moneda)}"
        )
        texto_total.value = (
            f"Total a acreditar (estimado): "
            f"{formato.formatear_moneda(calcular_total_acreditar(estado.lineas), estado.moneda)}"
        )

    filas_lineas = [
        _construir_fila_linea_nc(page, estado, linea, indice, actualizar_totales)
        for indice, linea in enumerate(estado.lineas)
    ]
    actualizar_totales()

    boton_anterior = ft.TextButton(content="Anterior")
    boton_siguiente = ft.Button(content="Siguiente")

    def al_anterior(e: ft.Event[ft.TextButton]) -> None:
        ir_a_paso(1)

    def al_siguiente(e: ft.Event[ft.Button]) -> None:
        errores = validacion_nota_credito.validar_paso2(estado)
        if errores:
            texto_error.value = errores.get(
                "lineas",
                "Revisá las cantidades a acreditar: deben ser mayores a 0 y no superar "
                "la cantidad facturada de cada línea.",
            )
            texto_error.visible = True
            page.update()
            return
        texto_error.visible = False
        ir_a_paso(3)

    boton_anterior.on_click = al_anterior
    boton_siguiente.on_click = al_siguiente

    return ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        controls=[
            ft.Text("Paso 2 — Líneas", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            ft.Text(
                "Seleccioná las líneas de la factura origen a acreditar y ajustá la "
                "cantidad si el crédito es parcial.",
                theme_style=ft.TextThemeStyle.BODY_SMALL,
                color=tokens.GRAFITO,
            ),
            ft.Column(spacing=12, controls=filas_lineas),
            ft.Divider(),
            texto_subtotal,
            texto_iva,
            texto_total,
            ft.Text(
                "El saldo disponible de la factura origen y el IVA definitivo los "
                "valida/calcula el sistema al emitir.",
                theme_style=ft.TextThemeStyle.BODY_SMALL,
                color=tokens.GRAFITO,
            ),
            texto_error,
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[boton_anterior, boton_siguiente],
            ),
        ],
    )
