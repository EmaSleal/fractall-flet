from datetime import datetime
from typing import Callable, Optional

import flet as ft

import catalogos
import formato
import router_query
import rutas
import validacion
from api.cliente import ApiFallo
from api.cliente_autenticado import SesionExpirada
from api.clientes import (
    ClienteExoneracion,
    DatosExoneracion,
    crear_exoneracion,
    desactivar_exoneracion,
    listar_exoneraciones,
)
from diseno import tokens
from ui.componentes.badge import construir_badge
from ui.componentes.shell_protegido import construir_vista_protegida


def _fila_exoneracion(
    ex: ClienteExoneracion, al_desactivar: Callable[[ClienteExoneracion], None]
) -> ft.Container:
    acciones = []
    if ex.activo:
        acciones.append(
            ft.TextButton(
                content="Desactivar", on_click=lambda e: al_desactivar(ex)
            )
        )
    return ft.Container(
        border=ft.Border.all(1, tokens.ARENA),
        border_radius=tokens.RADIO_LG,
        bgcolor=tokens.LINO,
        padding=16,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Column(
                    spacing=4,
                    expand=True,
                    controls=[
                        ft.Text(
                            catalogos.label_tipo_exoneracion(ex.tipo_documento),
                            theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                        ),
                        ft.Text(
                            f"N.° documento: {ex.numero_documento or '—'}",
                            theme_style=ft.TextThemeStyle.BODY_SMALL,
                            color=tokens.GRAFITO,
                        ),
                        ft.Text(
                            f"{ex.porcentaje_exoneracion}% · Vence: "
                            f"{formato.formatear_fecha(ex.fecha_vencimiento)}",
                            theme_style=ft.TextThemeStyle.BODY_SMALL,
                            color=tokens.GRAFITO,
                        ),
                        ft.Row(
                            spacing=8,
                            controls=[
                                construir_badge(
                                    "Activo" if ex.activo else "Inactivo",
                                    tokens.ESTADO_ACEPTADO
                                    if ex.activo
                                    else tokens.GRAFITO,
                                    compacto=True,
                                ),
                                construir_badge(
                                    "Vigente" if ex.vigente else "No vigente",
                                    tokens.ESTADO_ACEPTADO
                                    if ex.vigente
                                    else tokens.ESTADO_PENDIENTE,
                                    compacto=True,
                                ),
                            ],
                        ),
                    ],
                ),
                ft.Column(controls=acciones),
            ],
        ),
    )


def _campo_fecha(page: ft.Page, etiqueta: str, requerido: bool) -> tuple[ft.Row, dict]:
    estado = {"valor": None}
    texto = ft.Text(
        "Sin seleccionar" if not requerido else "Sin seleccionar (requerido)",
        theme_style=ft.TextThemeStyle.BODY_MEDIUM,
    )

    def al_elegir(e: ft.Event[ft.DatePicker]) -> None:
        if picker.value:
            estado["valor"] = picker.value
            texto.value = picker.value.strftime("%d/%m/%Y")
            page.update()

    picker = ft.DatePicker(
        first_date=datetime(2000, 1, 1),
        last_date=datetime(2100, 1, 1),
        on_change=al_elegir,
    )

    fila = ft.Row(
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text(f"{etiqueta}:", theme_style=ft.TextThemeStyle.LABEL_LARGE),
            texto,
            ft.IconButton(
                icon=ft.Icons.CALENDAR_MONTH,
                on_click=lambda e: page.show_dialog(picker),
            ),
        ],
    )
    return fila, estado


def vista_clientes_exoneraciones(page: ft.Page) -> ft.View:
    id_cliente = router_query.parametro(page.route, "id")

    texto_estado = ft.Text("Cargando...", theme_style=ft.TextThemeStyle.BODY_SMALL)
    texto_error = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    texto_vacio = ft.Text(
        "Sin exoneraciones registradas",
        theme_style=ft.TextThemeStyle.BODY_MEDIUM,
        visible=False,
    )
    lista_exoneraciones = ft.Column(spacing=8)
    interruptor_vigentes = ft.Switch(label="Solo vigentes", value=False)

    # --- formulario "Nueva exoneración" ---
    campo_tipo_documento = ft.Dropdown(
        label="Tipo de documento",
        options=[
            ft.DropdownOption(key=valor, text=catalogos.label_tipo_exoneracion(valor))
            for valor, _etiqueta, _no_aplica in catalogos.TIPOS_EXONERACION
        ],
    )
    campo_numero_documento = ft.TextField(label="Número de documento", max_length=40)
    campo_nombre_institucion = ft.TextField(
        label="Nombre de la institución", max_length=160
    )
    campo_numero_articulo = ft.TextField(label="Número de artículo", max_length=10)
    campo_inciso = ft.TextField(label="Inciso", max_length=10)
    campo_nombre_institucion_otros = ft.TextField(
        label='Institución (detalle para tipo "99 — Otros")', max_length=160
    )
    campo_porcentaje = ft.TextField(
        label="Porcentaje de exoneración", keyboard_type=ft.KeyboardType.NUMBER
    )
    fila_fecha_emision, estado_fecha_emision = _campo_fecha(
        page, "Fecha de emisión", requerido=True
    )
    fila_fecha_vencimiento, estado_fecha_vencimiento = _campo_fecha(
        page, "Fecha de vencimiento", requerido=False
    )
    texto_error_form = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    boton_crear = ft.Button(content="Agregar exoneración")

    def mostrar_error_form(mensaje: str) -> None:
        texto_error_form.value = mensaje
        texto_error_form.visible = True
        page.update()

    def limpiar_errores_form() -> None:
        for campo in (
            campo_numero_documento,
            campo_nombre_institucion,
            campo_nombre_institucion_otros,
            campo_porcentaje,
        ):
            campo.error = None
        campo_tipo_documento.error_text = None
        texto_error_form.visible = False

    async def cargar_lista() -> None:
        if not id_cliente:
            texto_estado.visible = False
            texto_error.value = "Cliente no especificado."
            texto_error.visible = True
            page.update()
            return

        texto_estado.visible = True
        texto_error.visible = False
        texto_vacio.visible = False
        page.update()

        try:
            resultado = await listar_exoneraciones(
                id_cliente, solo_vigentes=interruptor_vigentes.value
            )
        except SesionExpirada:
            page.navigate(rutas.LOGIN)
            return
        texto_estado.visible = False

        if isinstance(resultado, ApiFallo):
            texto_error.value = resultado.error.mensaje
            texto_error.visible = True
            page.update()
            return

        exoneraciones = resultado.datos
        if not exoneraciones:
            lista_exoneraciones.controls = []
            texto_vacio.visible = True
        else:
            lista_exoneraciones.controls = [
                _fila_exoneracion(ex, al_pedir_desactivar) for ex in exoneraciones
            ]
        page.update()

    def al_pedir_desactivar(ex: ClienteExoneracion) -> None:
        async def confirmar(e: ft.Event[ft.TextButton]) -> None:
            page.pop_dialog()
            try:
                resultado = await desactivar_exoneracion(ex.id)
            except SesionExpirada:
                page.navigate(rutas.LOGIN)
                return
            if isinstance(resultado, ApiFallo):
                texto_error.value = resultado.error.mensaje
                texto_error.visible = True
                page.update()
                return
            await cargar_lista()

        def cancelar(e: ft.Event[ft.TextButton]) -> None:
            page.pop_dialog()

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("Desactivar exoneración"),
            content=ft.Text(
                "¿Desactivar esta exoneración? Esta acción no se puede deshacer."
            ),
            actions=[
                ft.TextButton(content="Cancelar", on_click=cancelar),
                ft.TextButton(content="Desactivar", on_click=confirmar),
            ],
        )
        page.show_dialog(dialogo)

    async def al_cambiar_filtro(e: ft.Event[ft.Switch]) -> None:
        await cargar_lista()

    interruptor_vigentes.on_change = al_cambiar_filtro

    async def al_crear(e: ft.Event[ft.Button]) -> None:
        limpiar_errores_form()
        page.update()

        valido = True
        if not campo_tipo_documento.value:
            campo_tipo_documento.error_text = "Seleccioná un tipo"
            valido = False
        if not campo_numero_documento.value.strip():
            campo_numero_documento.error = "Requerido"
            valido = False
        if not campo_nombre_institucion.value.strip():
            campo_nombre_institucion.error = "Requerido"
            valido = False
        error_institucion_otros = validacion.exoneracion_requiere_institucion_otros(
            campo_tipo_documento.value or "", campo_nombre_institucion_otros.value
        )
        if error_institucion_otros:
            campo_nombre_institucion_otros.error = error_institucion_otros
            valido = False
        if not estado_fecha_emision["valor"]:
            mostrar_error_form("Seleccioná la fecha de emisión.")
            valido = False

        try:
            porcentaje = float(campo_porcentaje.value.replace(",", "."))
            if not (0 <= porcentaje <= 100):
                raise ValueError
        except (ValueError, AttributeError):
            campo_porcentaje.error = "Debe ser un número entre 0 y 100"
            valido = False
            porcentaje = 0

        if not valido:
            page.update()
            return

        boton_crear.disabled = True
        boton_crear.content = "Agregando..."
        page.update()

        datos = DatosExoneracion(
            tipo_documento=campo_tipo_documento.value,
            numero_documento=campo_numero_documento.value,
            nombre_institucion=campo_nombre_institucion.value,
            numero_articulo=campo_numero_articulo.value,
            inciso=campo_inciso.value,
            nombre_institucion_otros=campo_nombre_institucion_otros.value,
            fecha_emision=formato.fecha_a_iso(estado_fecha_emision["valor"]),
            fecha_vencimiento=(
                formato.fecha_a_iso(estado_fecha_vencimiento["valor"])
                if estado_fecha_vencimiento["valor"]
                else ""
            ),
            porcentaje_exoneracion=porcentaje,
        )

        try:
            resultado = await crear_exoneracion(id_cliente, datos)
        except SesionExpirada:
            page.navigate(rutas.LOGIN)
            return

        boton_crear.disabled = False
        boton_crear.content = "Agregar exoneración"

        if isinstance(resultado, ApiFallo):
            mostrar_error_form(resultado.error.mensaje)
            return

        for campo in (
            campo_numero_documento,
            campo_nombre_institucion,
            campo_numero_articulo,
            campo_inciso,
            campo_nombre_institucion_otros,
            campo_porcentaje,
        ):
            campo.value = ""
        campo_tipo_documento.value = None
        estado_fecha_emision["valor"] = None
        estado_fecha_vencimiento["valor"] = None
        fila_fecha_emision.controls[1].value = "Sin seleccionar (requerido)"
        fila_fecha_vencimiento.controls[1].value = "Sin seleccionar"

        await cargar_lista()

    boton_crear.on_click = al_crear
    for campo in (
        campo_numero_documento,
        campo_nombre_institucion,
        campo_numero_articulo,
        campo_inciso,
        campo_nombre_institucion_otros,
        campo_porcentaje,
    ):
        campo.on_submit = al_crear

    page.run_task(cargar_lista)

    contenido_pagina = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Exoneraciones", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
                    ft.TextButton(
                        content="Volver al cliente",
                        on_click=lambda e: page.navigate(
                            rutas.CLIENTES_DETALLE, id=id_cliente or ""
                        ),
                    ),
                ],
            ),
            interruptor_vigentes,
            texto_estado,
            texto_error,
            texto_vacio,
            lista_exoneraciones,
            ft.Divider(),
            ft.Text("Nueva exoneración", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            campo_tipo_documento,
            campo_numero_documento,
            campo_nombre_institucion,
            campo_numero_articulo,
            campo_inciso,
            campo_nombre_institucion_otros,
            fila_fecha_emision,
            fila_fecha_vencimiento,
            campo_porcentaje,
            texto_error_form,
            boton_crear,
        ],
    )

    return construir_vista_protegida(
        page, rutas.CLIENTES_EXONERACIONES, rutas.CLIENTES, contenido_pagina
    )
