from typing import Callable

import flet as ft

import catalogos
import formato
import rutas
from api.cliente import ApiFallo
from api.cliente_autenticado import SesionExpirada
from api.facturas import crear_nota_credito
from diseno import tokens
from estado_nota_credito import (
    EstadoNotaCredito,
    calcular_iva_total_acreditar,
    calcular_subtotal_acreditar,
    calcular_subtotal_total_acreditar,
    calcular_total_acreditar,
)
from parsear_error_servidor_nota_credito import parsear_error_servidor_nota_credito


def construir_paso3(
    page: ft.Page, estado: EstadoNotaCredito, ir_a_paso: Callable[[int], None]
) -> ft.Column:
    lineas_seleccionadas = [linea for linea in estado.lineas if linea.seleccionada]

    subtotal = calcular_subtotal_total_acreditar(estado.lineas)
    iva = calcular_iva_total_acreditar(estado.lineas)
    total = calcular_total_acreditar(estado.lineas)

    filas_lineas = [
        ft.Text(
            f"#{linea.numero_linea} · CABYS {linea.codigo_cabys_aplicado or '—'} — "
            f"{linea.cantidad_acreditar} de {linea.cantidad_origen} "
            f"{linea.unidad_medida_comercial or ''} = "
            f"{formato.formatear_moneda(calcular_subtotal_acreditar(linea), estado.moneda)}",
            theme_style=ft.TextThemeStyle.BODY_SMALL,
            font_family=tokens.FUENTE_MONO,
        )
        for linea in lineas_seleccionadas
    ]

    controles_motivo_otro = (
        [
            ft.Text(
                f"Descripción del motivo: {estado.codigo_referencia_otro}",
                theme_style=ft.TextThemeStyle.BODY_SMALL,
                color=tokens.GRAFITO,
            )
        ]
        if estado.codigo_referencia == "99" and estado.codigo_referencia_otro
        else []
    )
    controles_razon = (
        [
            ft.Text(
                f"Razón: {estado.razon}",
                theme_style=ft.TextThemeStyle.BODY_SMALL,
                color=tokens.GRAFITO,
            )
        ]
        if estado.razon
        else []
    )

    texto_error = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    boton_emitir = ft.Button(content="Emitir nota de crédito")
    boton_anterior = ft.TextButton(content="Anterior")

    async def al_emitir(e: ft.Event[ft.Button]) -> None:
        texto_error.visible = False
        boton_emitir.disabled = True
        boton_emitir.content = "Emitiendo..."
        page.update()

        try:
            resultado = await crear_nota_credito(estado.a_cuerpo_creacion())
        except SesionExpirada:
            page.navigate(rutas.LOGIN)
            return

        if isinstance(resultado, ApiFallo):
            error_wizard = parsear_error_servidor_nota_credito(
                resultado.error.status, resultado.error.mensaje
            )
            estado.error_servidor = error_wizard

            boton_emitir.disabled = False
            boton_emitir.content = "Emitir nota de crédito"
            texto_error.value = error_wizard.mensaje
            texto_error.visible = True
            page.update()

            if error_wizard.paso != 3:
                ir_a_paso(error_wizard.paso)
            return

        page.navigate(rutas.FACTURAS_DETALLE, id=resultado.datos.id)

    boton_emitir.on_click = al_emitir
    boton_anterior.on_click = lambda e: ir_a_paso(2)

    return ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        controls=[
            ft.Text("Paso 3 — Confirmación", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            ft.Text(
                f"Corrige a: {estado.factura_origen_consecutivo}",
                theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                font_family=tokens.FUENTE_MONO,
            ),
            ft.Text(
                f"Cliente: {estado.cliente_nombre}",
                theme_style=ft.TextThemeStyle.BODY_MEDIUM,
            ),
            ft.Text(
                f"Código de referencia: {estado.codigo_referencia} — "
                f"{catalogos.label_codigo_referencia(estado.codigo_referencia)}",
                theme_style=ft.TextThemeStyle.BODY_SMALL,
                color=tokens.GRAFITO,
            ),
            *controles_motivo_otro,
            *controles_razon,
            ft.Divider(),
            ft.Text("Líneas a acreditar", theme_style=ft.TextThemeStyle.LABEL_LARGE),
            *filas_lineas,
            ft.Divider(),
            ft.Text(
                f"Subtotal: {formato.formatear_moneda(subtotal, estado.moneda)}",
                theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                font_family=tokens.FUENTE_MONO,
            ),
            ft.Text(
                f"IVA (estimado): {formato.formatear_moneda(iva, estado.moneda)}",
                theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                font_family=tokens.FUENTE_MONO,
            ),
            ft.Text(
                f"Total: {formato.formatear_moneda(total, estado.moneda)}",
                theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                font_family=tokens.FUENTE_MONO,
            ),
            ft.Text(
                "El total mostrado es una estimación — el sistema valida el saldo "
                "disponible de la factura origen y calcula el valor final al procesar "
                "la nota de crédito.",
                theme_style=ft.TextThemeStyle.BODY_SMALL,
                color=tokens.GRAFITO,
            ),
            texto_error,
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[boton_anterior, boton_emitir],
            ),
        ],
    )
