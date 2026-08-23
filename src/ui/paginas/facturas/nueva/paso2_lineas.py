from typing import Callable

import flet as ft

import calculo_factura
import formato
import validacion_factura
from api.productos import Producto, buscar_productos
from diseno import tokens
from estado_factura import EstadoFactura, LineaWizard
from ui.componentes.buscador_remoto import construir_buscador_remoto


def _texto_producto(p: Producto) -> str:
    return f"{p.codigo} — {p.descripcion}"


def construir_fila_linea(
    page: ft.Page,
    estado: EstadoFactura,
    linea: LineaWizard,
    al_eliminar: Callable[[], None],
    es_unica: bool,
) -> ft.Container:
    """Público — el wizard de Tiquete (venta de mostrador, sin línea de
    factura origen) reusa esta fila tal cual, solo cambia la orquestación
    del paso (ver facturas/tiquetes/nueva/paso2_lineas.py)."""
    texto_subtotal = ft.Text(
        theme_style=ft.TextThemeStyle.BODY_SMALL, font_family=tokens.FUENTE_MONO
    )

    def refrescar_subtotal() -> None:
        subtotal = calculo_factura.calcular_subtotal_linea(
            linea.cantidad, linea.precio_unitario, linea.descuento_monto
        )
        texto_subtotal.value = f"Subtotal: {formato.formatear_moneda(subtotal)}"

    async def al_elegir_producto(producto: Producto) -> None:
        linea.producto_id = producto.id
        linea.producto_descripcion = producto.descripcion
        linea.precio_unitario = producto.precio_venta
        linea.porcentaje_impuesto = producto.porcentaje_impuesto
        campo_precio.value = str(producto.precio_venta)
        refrescar_subtotal()
        page.update()

    buscador_producto = construir_buscador_remoto(
        page,
        etiqueta="Producto",
        buscar=buscar_productos,
        renderizar_opcion=_texto_producto,
        al_seleccionar=lambda p: page.run_task(al_elegir_producto, p),
        valor_inicial=linea.producto_descripcion,
        pista="Buscá por código o descripción",
    )

    campo_cantidad = ft.TextField(
        label="Cantidad", keyboard_type=ft.KeyboardType.NUMBER, value=str(linea.cantidad)
    )
    campo_precio = ft.TextField(
        label="Precio unitario",
        keyboard_type=ft.KeyboardType.NUMBER,
        value=str(linea.precio_unitario),
    )

    def al_cambiar_cantidad(e: ft.Event[ft.TextField]) -> None:
        try:
            linea.cantidad = float(campo_cantidad.value)
        except ValueError:
            linea.cantidad = 0
        refrescar_subtotal()
        page.update()

    def al_cambiar_precio(e: ft.Event[ft.TextField]) -> None:
        try:
            linea.precio_unitario = float(campo_precio.value)
        except ValueError:
            linea.precio_unitario = 0
        refrescar_subtotal()
        page.update()

    campo_cantidad.on_change = al_cambiar_cantidad
    campo_precio.on_change = al_cambiar_precio

    campo_descuento_monto = ft.TextField(
        label="Monto de descuento",
        keyboard_type=ft.KeyboardType.NUMBER,
        value=str(linea.descuento_monto) if linea.descuento_monto else "",
    )
    campo_descuento_razon = ft.TextField(
        label="Razón del descuento", value=linea.descuento_razon
    )

    def al_cambiar_descuento(e: ft.Event[ft.TextField]) -> None:
        try:
            linea.descuento_monto = float(campo_descuento_monto.value or 0)
        except ValueError:
            linea.descuento_monto = 0
        linea.descuento_razon = campo_descuento_razon.value
        refrescar_subtotal()
        page.update()

    campo_descuento_monto.on_change = al_cambiar_descuento
    campo_descuento_razon.on_change = al_cambiar_descuento

    controles_exoneracion = []
    if estado.exoneraciones_vigentes:
        opciones = [ft.DropdownOption(key="__ninguna__", text="Ninguna")] + [
            ft.DropdownOption(key=ex.id, text=ex.descripcion)
            for ex in estado.exoneraciones_vigentes
        ]

        def al_cambiar_exoneracion(e: ft.Event[ft.Dropdown]) -> None:
            valor = campo_exoneracion.value
            linea.exoneracion_id = None if valor == "__ninguna__" else valor

        campo_exoneracion = ft.Dropdown(
            label="Exoneración",
            value=linea.exoneracion_id or "__ninguna__",
            options=opciones,
            on_select=al_cambiar_exoneracion,
        )
        controles_exoneracion = [campo_exoneracion]

    refrescar_subtotal()

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
                        ft.Text("Línea", theme_style=ft.TextThemeStyle.LABEL_LARGE),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            disabled=es_unica,
                            on_click=lambda e: al_eliminar(),
                        ),
                    ],
                ),
                buscador_producto,
                ft.ResponsiveRow(
                    controls=[
                        ft.Container(col={"xs": 12, "sm": 6}, content=campo_cantidad),
                        ft.Container(col={"xs": 12, "sm": 6}, content=campo_precio),
                    ]
                ),
                ft.ResponsiveRow(
                    controls=[
                        ft.Container(col={"xs": 12, "sm": 6}, content=campo_descuento_monto),
                        ft.Container(col={"xs": 12, "sm": 6}, content=campo_descuento_razon),
                    ]
                ),
                *controles_exoneracion,
                texto_subtotal,
            ],
        ),
    )


def construir_paso2(
    page: ft.Page, estado: EstadoFactura, ir_a_paso: Callable[[int], None]
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
        errores = validacion_factura.validar_paso2(estado)
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
