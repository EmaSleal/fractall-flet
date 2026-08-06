from typing import Callable

import flet as ft

import calculo_factura
import catalogos
import formato
import rutas
from api.cliente import ApiFallo
from api.cliente_autenticado import SesionExpirada
from api.facturas import crear_factura
from diseno import tokens
from estado_factura import EstadoFactura
from parsear_error_servidor import parsear_error_servidor


def construir_paso4(
    page: ft.Page, estado: EstadoFactura, ir_a_paso: Callable[[int], None]
) -> ft.Column:
    subtotal = calculo_factura.calcular_subtotal_factura(estado.lineas)
    iva = calculo_factura.calcular_iva_total(estado.lineas)
    total = calculo_factura.calcular_total_factura(estado.lineas, estado.otros_cargos)

    filas_lineas = [
        ft.Text(
            f"{linea.producto_descripcion or linea.producto_id} — "
            f"{linea.cantidad} × {formato.formatear_moneda(linea.precio_unitario, estado.moneda)}",
            theme_style=ft.TextThemeStyle.BODY_SMALL,
            font_family=tokens.FUENTE_MONO,
        )
        for linea in estado.lineas
    ]

    filas_medios = [
        ft.Text(
            f"{catalogos.label_tipo_medio_pago(m.tipo_medio_pago)}"
            f"{(' — ' + m.medio_pago_otros) if m.tipo_medio_pago == '99' else ''}: "
            f"{formato.formatear_moneda(m.total_medio_pago, estado.moneda)}",
            theme_style=ft.TextThemeStyle.BODY_SMALL,
            font_family=tokens.FUENTE_MONO,
        )
        for m in estado.medios_pago
    ]

    texto_error = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    boton_emitir = ft.Button(content="Emitir factura")
    boton_anterior = ft.TextButton(content="Anterior")

    async def al_emitir(e: ft.Event[ft.Button]) -> None:
        texto_error.visible = False
        boton_emitir.disabled = True
        boton_emitir.content = "Emitiendo..."
        page.update()

        try:
            resultado = await crear_factura(estado.a_cuerpo_creacion())
        except SesionExpirada:
            page.navigate(rutas.LOGIN)
            return

        if isinstance(resultado, ApiFallo):
            error_wizard = parsear_error_servidor(
                resultado.error.status, resultado.error.mensaje
            )
            estado.error_servidor = error_wizard

            boton_emitir.disabled = False
            boton_emitir.content = "Emitir factura"
            texto_error.value = error_wizard.mensaje
            texto_error.visible = True
            page.update()

            if error_wizard.paso != 4:
                ir_a_paso(error_wizard.paso)
            return

        page.navigate(rutas.FACTURAS_DETALLE, id=resultado.datos.id)

    boton_emitir.on_click = al_emitir
    boton_anterior.on_click = lambda e: ir_a_paso(3)

    return ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        controls=[
            ft.Text("Paso 4 — Confirmación", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            ft.Text(
                f"Cliente: {estado.cliente_nombre}", theme_style=ft.TextThemeStyle.BODY_MEDIUM
            ),
            ft.Text(
                f"Condición de venta: {catalogos.label_condicion_venta(estado.condicion_venta)}",
                theme_style=ft.TextThemeStyle.BODY_SMALL,
                color=tokens.GRAFITO,
            ),
            ft.Text(
                f"Moneda: {estado.moneda}"
                + (f" (tipo de cambio ₡{estado.tipo_cambio})" if estado.moneda == "USD" else ""),
                theme_style=ft.TextThemeStyle.BODY_SMALL,
                color=tokens.GRAFITO,
            ),
            ft.Divider(),
            ft.Text("Líneas", theme_style=ft.TextThemeStyle.LABEL_LARGE),
            *filas_lineas,
            ft.Divider(),
            ft.Text("Medios de pago", theme_style=ft.TextThemeStyle.LABEL_LARGE),
            *filas_medios,
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
                "El IVA mostrado es una estimación — Hacienda calcula el valor final "
                "al procesar la factura.",
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
