from typing import Callable

import flet as ft

import catalogos
import rutas
import validacion_factura
from api.clientes import Cliente, buscar_clientes, listar_exoneraciones
from api.cliente import ApiFallo
from api.cliente_autenticado import SesionExpirada
from api.tipo_cambio import obtener_tipo_cambio_dolar
from diseno import tokens
from estado_factura import EstadoFactura, ExoneracionVigenteItem
from ui.componentes.buscador_remoto import construir_buscador_remoto


def _texto_cliente(c: Cliente) -> str:
    return f"{c.nombre} — {catalogos.label_tipo_identificacion(c.tipo_identificacion)} {c.numero_identificacion}"


def construir_paso1(
    page: ft.Page, estado: EstadoFactura, ir_a_paso: Callable[[int], None]
) -> ft.Column:
    texto_cliente_elegido = ft.Text(
        f"Cliente elegido: {estado.cliente_nombre}" if estado.cliente_nombre else "",
        theme_style=ft.TextThemeStyle.BODY_SMALL,
        color=tokens.ESTADO_ACEPTADO,
        visible=bool(estado.cliente_nombre),
    )

    async def al_elegir_cliente(cliente: Cliente) -> None:
        estado.establecer_cliente(cliente.id, cliente.nombre, cliente.numero_identificacion)
        texto_cliente_elegido.value = f"Cliente elegido: {cliente.nombre}"
        texto_cliente_elegido.visible = True
        page.update()

        try:
            resultado = await listar_exoneraciones(cliente.id, solo_vigentes=True)
        except SesionExpirada:
            page.navigate(rutas.LOGIN)
            return
        if not isinstance(resultado, ApiFallo):
            estado.establecer_exoneraciones_vigentes(
                [
                    ExoneracionVigenteItem(
                        id=ex.id,
                        descripcion=f"{catalogos.label_tipo_exoneracion(ex.tipo_documento)} "
                        f"({ex.porcentaje_exoneracion}%)",
                    )
                    for ex in resultado.datos
                ]
            )

    buscador_cliente = construir_buscador_remoto(
        page,
        etiqueta="Cliente",
        buscar=buscar_clientes,
        renderizar_opcion=_texto_cliente,
        al_seleccionar=lambda c: page.run_task(al_elegir_cliente, c),
        pista="Buscá por nombre o identificación",
    )

    campo_condicion_venta = ft.Dropdown(
        label="Condición de venta",
        value=estado.condicion_venta,
        options=[
            ft.DropdownOption(key=clave, text=f"{clave} — {etiqueta}")
            for clave, etiqueta in catalogos.CONDICIONES_VENTA
        ],
    )
    campo_plazo_credito = ft.TextField(
        label="Plazo de crédito (días)",
        keyboard_type=ft.KeyboardType.NUMBER,
        value=str(estado.plazo_credito) if estado.plazo_credito else "",
        visible=estado.condicion_venta == "02",
    )
    campo_condicion_venta_otros = ft.TextField(
        label="Detalle de la condición de venta",
        value=estado.condicion_venta_otros,
        visible=estado.condicion_venta == "99",
    )

    async def al_cambiar_condicion_venta(e: ft.Event[ft.Dropdown]) -> None:
        estado.establecer_condicion_venta(campo_condicion_venta.value)
        campo_plazo_credito.visible = estado.condicion_venta == "02"
        campo_condicion_venta_otros.visible = estado.condicion_venta == "99"
        page.update()

    campo_condicion_venta.on_select = al_cambiar_condicion_venta

    campo_moneda = ft.Dropdown(
        label="Moneda",
        value=estado.moneda,
        options=[
            ft.DropdownOption(key=clave, text=etiqueta) for clave, etiqueta in catalogos.MONEDAS
        ],
    )
    campo_tipo_cambio = ft.TextField(
        label="Tipo de cambio (₡ por USD)",
        keyboard_type=ft.KeyboardType.NUMBER,
        value=str(estado.tipo_cambio),
        visible=estado.moneda == "USD",
    )

    async def al_cambiar_moneda(e: ft.Event[ft.Dropdown]) -> None:
        estado.establecer_moneda(campo_moneda.value)
        campo_tipo_cambio.visible = estado.moneda == "USD"
        campo_tipo_cambio.value = str(estado.tipo_cambio)
        page.update()

        if estado.moneda == "USD":
            valor = await obtener_tipo_cambio_dolar()
            # el usuario pudo haber cambiado de moneda de nuevo mientras esperábamos
            if valor is not None and campo_moneda.value == "USD":
                campo_tipo_cambio.value = str(valor)
                page.update()

    campo_moneda.on_select = al_cambiar_moneda

    texto_error = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    boton_siguiente = ft.Button(content="Siguiente")

    def limpiar_errores() -> None:
        for campo in (campo_plazo_credito, campo_condicion_venta_otros, campo_tipo_cambio):
            campo.error = None
        campo_condicion_venta.error_text = None
        campo_moneda.error_text = None
        texto_error.visible = False

    async def al_siguiente(e: ft.Event[ft.Button]) -> None:
        limpiar_errores()

        try:
            estado.plazo_credito = (
                int(campo_plazo_credito.value) if campo_plazo_credito.value.strip() else None
            )
        except ValueError:
            estado.plazo_credito = None
        estado.condicion_venta_otros = campo_condicion_venta_otros.value
        try:
            estado.tipo_cambio = (
                float(campo_tipo_cambio.value) if campo_tipo_cambio.value.strip() else 0.0
            )
        except ValueError:
            estado.tipo_cambio = 0.0

        errores = validacion_factura.validar_paso1(estado)
        if errores:
            mapa = {
                "plazo_credito": campo_plazo_credito,
                "condicion_venta_otros": campo_condicion_venta_otros,
                "tipo_cambio": campo_tipo_cambio,
            }
            for clave, mensaje in errores.items():
                if clave == "cliente_id":
                    texto_error.value = mensaje
                    texto_error.visible = True
                elif clave in mapa:
                    mapa[clave].error = mensaje
            page.update()
            return

        ir_a_paso(2)

    boton_siguiente.on_click = al_siguiente
    campo_plazo_credito.on_submit = al_siguiente
    campo_condicion_venta_otros.on_submit = al_siguiente
    campo_tipo_cambio.on_submit = al_siguiente

    return ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        controls=[
            ft.Text("Paso 1 — Cliente", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            buscador_cliente,
            texto_cliente_elegido,
            campo_condicion_venta,
            campo_plazo_credito,
            campo_condicion_venta_otros,
            campo_moneda,
            campo_tipo_cambio,
            texto_error,
            ft.Row(alignment=ft.MainAxisAlignment.END, controls=[boton_siguiente]),
        ],
    )
