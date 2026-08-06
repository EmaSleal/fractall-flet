from typing import Callable

import flet as ft

import calculo_factura
import catalogos
import formato
from diseno import tokens
from estado_factura import EstadoFactura, MedioPagoWizard, OtroCargoWizard


def _construir_fila_medio_pago(
    page: ft.Page,
    medio: MedioPagoWizard,
    al_eliminar: Callable[[], None],
    al_cambiar: Callable[[], None],
) -> ft.Container:
    campo_tipo = ft.Dropdown(
        label="Tipo de medio de pago",
        value=medio.tipo_medio_pago or None,
        options=[
            ft.DropdownOption(key=clave, text=etiqueta)
            for clave, etiqueta in catalogos.TIPOS_MEDIO_PAGO
        ],
    )
    campo_otros = ft.TextField(
        label="Detalle (medio de pago \"Otros\")",
        value=medio.medio_pago_otros,
        visible=medio.tipo_medio_pago == "99",
    )
    campo_monto = ft.TextField(
        label="Monto",
        keyboard_type=ft.KeyboardType.NUMBER,
        value=str(medio.total_medio_pago) if medio.total_medio_pago else "",
    )

    def al_cambiar_tipo(e: ft.Event[ft.Dropdown]) -> None:
        medio.tipo_medio_pago = campo_tipo.value or ""
        campo_otros.visible = medio.tipo_medio_pago == "99"
        page.update()
        al_cambiar()

    def al_cambiar_otros(e: ft.Event[ft.TextField]) -> None:
        medio.medio_pago_otros = campo_otros.value
        al_cambiar()

    def al_cambiar_monto(e: ft.Event[ft.TextField]) -> None:
        try:
            medio.total_medio_pago = float(campo_monto.value or 0)
        except ValueError:
            medio.total_medio_pago = 0
        al_cambiar()

    campo_tipo.on_select = al_cambiar_tipo
    campo_otros.on_change = al_cambiar_otros
    campo_monto.on_change = al_cambiar_monto

    return ft.Container(
        border=ft.Border.all(1, tokens.ARENA),
        border_radius=tokens.RADIO_LG,
        padding=16,
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Medio de pago", theme_style=ft.TextThemeStyle.LABEL_LARGE),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE, on_click=lambda e: al_eliminar()
                        ),
                    ],
                ),
                campo_tipo,
                campo_otros,
                campo_monto,
            ],
        ),
    )


def _construir_fila_otro_cargo(
    page: ft.Page, cargo: OtroCargoWizard, al_eliminar: Callable[[], None]
) -> ft.Container:
    campo_tipo = ft.Dropdown(
        label="Tipo de cargo",
        value=cargo.tipo_documento_oc or None,
        options=[
            ft.DropdownOption(key=clave, text=etiqueta)
            for clave, etiqueta in catalogos.TIPOS_DOCUMENTO_OC
        ],
    )
    campo_otros = ft.TextField(
        label="Detalle (tipo \"Otros\")",
        value=cargo.tipo_documento_otros,
        visible=cargo.tipo_documento_oc == "99",
    )
    campo_detalle = ft.TextField(label="Detalle", value=cargo.detalle)
    campo_monto = ft.TextField(
        label="Monto", keyboard_type=ft.KeyboardType.NUMBER, value=str(cargo.monto_cargo)
    )

    def al_cambiar_tipo(e: ft.Event[ft.Dropdown]) -> None:
        cargo.tipo_documento_oc = campo_tipo.value or ""
        campo_otros.visible = cargo.tipo_documento_oc == "99"
        page.update()

    def al_cambiar_otros(e: ft.Event[ft.TextField]) -> None:
        cargo.tipo_documento_otros = campo_otros.value

    def al_cambiar_detalle(e: ft.Event[ft.TextField]) -> None:
        cargo.detalle = campo_detalle.value

    def al_cambiar_monto(e: ft.Event[ft.TextField]) -> None:
        try:
            cargo.monto_cargo = float(campo_monto.value or 0)
        except ValueError:
            cargo.monto_cargo = 0

    campo_tipo.on_select = al_cambiar_tipo
    campo_otros.on_change = al_cambiar_otros
    campo_detalle.on_change = al_cambiar_detalle
    campo_monto.on_change = al_cambiar_monto

    return ft.Container(
        border=ft.Border.all(1, tokens.ARENA),
        border_radius=tokens.RADIO_LG,
        padding=16,
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Otro cargo", theme_style=ft.TextThemeStyle.LABEL_LARGE),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE, on_click=lambda e: al_eliminar()
                        ),
                    ],
                ),
                campo_tipo,
                campo_otros,
                campo_detalle,
                campo_monto,
            ],
        ),
    )


def construir_paso3(
    page: ft.Page, estado: EstadoFactura, ir_a_paso: Callable[[int], None]
) -> ft.Column:
    contenedor_medios = ft.Column(spacing=12)
    contenedor_cargos = ft.Column(spacing=12)
    texto_resumen = ft.Text(theme_style=ft.TextThemeStyle.BODY_MEDIUM, font_family=tokens.FUENTE_MONO)
    texto_error = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    boton_siguiente = ft.Button(content="Siguiente")

    def total_factura() -> float:
        return calculo_factura.calcular_total_factura(estado.lineas, estado.otros_cargos)

    def recalcular() -> None:
        total = total_factura()
        total_pagado = calculo_factura.calcular_total_medios_pago(estado.medios_pago)
        coincide = calculo_factura.coincide_total_medios_pago(estado.medios_pago, total)

        texto_resumen.value = (
            f"Total a pagar: {formato.formatear_moneda(total, estado.moneda)}   ·   "
            f"Pagado: {formato.formatear_moneda(total_pagado, estado.moneda)}"
        )
        texto_resumen.color = tokens.ESTADO_ACEPTADO if coincide else tokens.ESTADO_RECHAZADO
        boton_siguiente.disabled = not coincide or not estado.medios_pago
        page.update()

    def renderizar_medios() -> None:
        contenedor_medios.controls = [
            _construir_fila_medio_pago(
                page, medio, al_eliminar=lambda i=i: eliminar_medio(i), al_cambiar=recalcular
            )
            for i, medio in enumerate(estado.medios_pago)
        ]
        page.update()

    def eliminar_medio(indice: int) -> None:
        del estado.medios_pago[indice]
        renderizar_medios()
        recalcular()

    def al_agregar_medio(e: ft.Event[ft.TextButton]) -> None:
        estado.medios_pago.append(MedioPagoWizard())
        renderizar_medios()
        recalcular()

    def renderizar_cargos() -> None:
        contenedor_cargos.controls = [
            _construir_fila_otro_cargo(page, cargo, al_eliminar=lambda i=i: eliminar_cargo(i))
            for i, cargo in enumerate(estado.otros_cargos)
        ]
        page.update()

    def eliminar_cargo(indice: int) -> None:
        del estado.otros_cargos[indice]
        renderizar_cargos()
        recalcular()

    def al_agregar_cargo(e: ft.Event[ft.TextButton]) -> None:
        estado.otros_cargos.append(OtroCargoWizard())
        renderizar_cargos()
        recalcular()

    def al_anterior(e: ft.Event[ft.TextButton]) -> None:
        ir_a_paso(2)

    def al_siguiente(e: ft.Event[ft.Button]) -> None:
        if boton_siguiente.disabled:
            return
        texto_error.visible = False
        ir_a_paso(4)

    boton_siguiente.on_click = al_siguiente

    renderizar_medios()
    renderizar_cargos()
    recalcular()

    return ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        controls=[
            ft.Text("Paso 3 — Medios de pago", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            texto_resumen,
            contenedor_medios,
            ft.TextButton(content="+ Agregar medio de pago", on_click=al_agregar_medio),
            ft.Divider(),
            ft.Text("Otros cargos (opcional)", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            contenedor_cargos,
            ft.TextButton(content="+ Agregar otro cargo", on_click=al_agregar_cargo),
            texto_error,
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.TextButton(content="Anterior", on_click=al_anterior),
                    boton_siguiente,
                ],
            ),
        ],
    )
