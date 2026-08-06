import flet as ft

import rutas
from api.cliente import ApiFallo
from api.cliente_autenticado import SesionExpirada
from api.productos import ProductoCreado, crear_producto
from api.unidades_medida import listar_unidades_medida
from diseno import tokens
from ui.componentes.shell_protegido import construir_vista_protegida
from ui.paginas.productos.formulario import construir_formulario_producto


def vista_productos_nuevo(page: ft.Page) -> ft.View:
    texto_estado = ft.Text("Cargando...", theme_style=ft.TextThemeStyle.BODY_SMALL)
    texto_error = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    contenedor_formulario = ft.Column(visible=False)

    async def cargar() -> None:
        try:
            resultado = await listar_unidades_medida()
        except SesionExpirada:
            page.navigate(rutas.LOGIN)
            return
        texto_estado.visible = False

        unidades = []
        if isinstance(resultado, ApiFallo):
            texto_error.value = (
                f"No se pudieron cargar las unidades de medida ({resultado.error.mensaje})"
                " — vas a poder escribirla a mano."
            )
            texto_error.visible = True
        else:
            unidades = resultado.datos

        def al_exito(creado: ProductoCreado) -> None:
            page.navigate(rutas.PRODUCTOS_DETALLE, id=creado.id)

        formulario = construir_formulario_producto(
            page, None, unidades, crear_producto, al_exito, texto_boton="Crear producto"
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
                    ft.Text("Nuevo producto", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
                    ft.TextButton(
                        content="Volver a productos",
                        on_click=lambda e: page.navigate(rutas.PRODUCTOS),
                    ),
                ],
            ),
            texto_estado,
            texto_error,
            contenedor_formulario,
        ],
    )

    return construir_vista_protegida(page, rutas.PRODUCTOS_NUEVO, rutas.PRODUCTOS, contenido_pagina)
