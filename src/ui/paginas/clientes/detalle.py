import flet as ft

import router_query
import rutas
from api.cliente import ApiFallo
from api.cliente_autenticado import SesionExpirada
from api.clientes import DatosCliente, actualizar_cliente, obtener_cliente
from diseno import tokens
from ui.componentes.shell_protegido import construir_vista_protegida
from ui.paginas.clientes.formulario import construir_formulario_cliente


def vista_clientes_detalle(page: ft.Page) -> ft.View:
    id_cliente = router_query.parametro(page.route, "id")

    texto_estado = ft.Text("Cargando...", theme_style=ft.TextThemeStyle.BODY_SMALL)
    texto_error_carga = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    texto_exito = ft.Text(value="", color=tokens.ESTADO_ACEPTADO, visible=False)
    contenedor_formulario = ft.Column(visible=False)

    async def cargar() -> None:
        if not id_cliente:
            texto_estado.visible = False
            texto_error_carga.value = "Cliente no especificado."
            texto_error_carga.visible = True
            page.update()
            return

        try:
            resultado = await obtener_cliente(id_cliente)
        except SesionExpirada:
            page.navigate(rutas.LOGIN)
            return
        texto_estado.visible = False

        if isinstance(resultado, ApiFallo):
            texto_error_carga.value = resultado.error.mensaje
            texto_error_carga.visible = True
            page.update()
            return

        cliente = resultado.datos
        if cliente is None:
            texto_error_carga.value = "Cliente no encontrado."
            texto_error_carga.visible = True
            page.update()
            return

        def al_exito(_datos: object) -> None:
            texto_exito.value = "Cliente actualizado."
            texto_exito.visible = True
            page.update()

        async def guardar(datos: DatosCliente):
            return await actualizar_cliente(id_cliente, datos)

        formulario = construir_formulario_cliente(
            page, cliente, guardar, al_exito, texto_boton="Guardar cambios"
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
                    ft.Text("Cliente", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
                    ft.TextButton(
                        content="Volver a clientes",
                        on_click=lambda e: page.navigate(rutas.CLIENTES),
                    ),
                ],
            ),
            ft.Row(
                controls=[
                    ft.Text(
                        "Datos del cliente",
                        theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                    ),
                    ft.TextButton(
                        content="Exoneraciones →",
                        on_click=lambda e: page.navigate(
                            rutas.CLIENTES_EXONERACIONES, id=id_cliente or ""
                        ),
                        disabled=not id_cliente,
                    ),
                ],
            ),
            texto_estado,
            texto_error_carga,
            texto_exito,
            contenedor_formulario,
        ],
    )

    return construir_vista_protegida(page, rutas.CLIENTES_DETALLE, rutas.CLIENTES, contenido_pagina)
