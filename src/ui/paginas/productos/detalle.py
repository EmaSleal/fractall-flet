import asyncio

import flet as ft

import router_query
import rutas
from api.cliente import ApiFallo
from api.cliente_autenticado import SesionExpirada
from api.productos import (
    DatosProducto,
    actualizar_producto,
    alternar_activo,
    obtener_producto,
)
from api.unidades_medida import listar_unidades_medida
from diseno import tokens
from ui.componentes.badge import construir_badge
from ui.componentes.shell_protegido import construir_vista_protegida
from ui.paginas.productos.formulario import construir_formulario_producto


def vista_productos_detalle(page: ft.Page) -> ft.View:
    id_producto = router_query.parametro(page.route, "id")

    texto_estado = ft.Text("Cargando...", theme_style=ft.TextThemeStyle.BODY_SMALL)
    texto_error_carga = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    texto_exito = ft.Text(value="", color=tokens.ESTADO_ACEPTADO, visible=False)
    contenedor_encabezado = ft.Row(visible=False)
    contenedor_formulario = ft.Column(visible=False)

    async def cargar() -> None:
        if not id_producto:
            texto_estado.visible = False
            texto_error_carga.value = "Producto no especificado."
            texto_error_carga.visible = True
            page.update()
            return

        try:
            resultado_producto, resultado_unidades = await asyncio.gather(
                obtener_producto(id_producto), listar_unidades_medida()
            )
        except SesionExpirada:
            page.navigate(rutas.LOGIN)
            return
        texto_estado.visible = False

        if isinstance(resultado_producto, ApiFallo):
            texto_error_carga.value = resultado_producto.error.mensaje
            texto_error_carga.visible = True
            page.update()
            return

        producto = resultado_producto.datos
        if producto is None:
            texto_error_carga.value = "Producto no encontrado."
            texto_error_carga.visible = True
            page.update()
            return

        unidades = [] if isinstance(resultado_unidades, ApiFallo) else resultado_unidades.datos

        boton_alternar = ft.TextButton(
            content="Desactivar producto" if producto.activo else "Activar producto"
        )

        async def al_alternar(e: ft.Event[ft.TextButton]) -> None:
            boton_alternar.disabled = True
            page.update()

            try:
                resultado = await alternar_activo(id_producto, not producto.activo)
            except SesionExpirada:
                page.navigate(rutas.LOGIN)
                return

            boton_alternar.disabled = False

            if isinstance(resultado, ApiFallo):
                texto_error_carga.value = resultado.error.mensaje
                texto_error_carga.visible = True
                page.update()
                return

            await cargar()

        boton_alternar.on_click = al_alternar

        contenedor_encabezado.controls = [
            ft.Text(producto.descripcion, theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
            ft.Row(
                controls=[
                    _badge_activo(producto.activo),
                    boton_alternar,
                ]
            ),
        ]
        contenedor_encabezado.visible = True

        def al_exito(_datos: object) -> None:
            texto_exito.value = "Producto actualizado."
            texto_exito.visible = True
            page.update()

        async def guardar(datos: DatosProducto):
            return await actualizar_producto(id_producto, datos)

        formulario = construir_formulario_producto(
            page, producto, unidades, guardar, al_exito, texto_boton="Guardar cambios"
        )
        contenedor_formulario.controls = [formulario]
        contenedor_formulario.visible = True
        page.update()

    page.run_task(cargar)

    contenido_pagina = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    contenedor_encabezado,
                    ft.TextButton(
                        content="Volver a productos",
                        on_click=lambda e: page.navigate(rutas.PRODUCTOS),
                    ),
                ],
            ),
            texto_estado,
            texto_error_carga,
            texto_exito,
            contenedor_formulario,
        ],
    )

    return construir_vista_protegida(page, rutas.PRODUCTOS_DETALLE, rutas.PRODUCTOS, contenido_pagina)


def _badge_activo(activo: bool) -> ft.Container:
    return construir_badge(
        "Activo" if activo else "Inactivo",
        tokens.ESTADO_ACEPTADO if activo else tokens.GRAFITO,
    )
