import flet as ft

import router_query
import rutas
from api.cliente import ApiFallo
from api.cliente_autenticado import SesionExpirada
from api.facturas import FacturaDetalle, obtener_factura
from diseno import tokens
from estado_nota_credito import EstadoNotaCredito, lineas_seleccionables_desde_factura
from ui.componentes.shell_protegido import construir_vista_protegida
from ui.paginas.facturas.nota_credito.nueva.paso1_motivo import construir_paso1
from ui.paginas.facturas.nota_credito.nueva.paso2_lineas import construir_paso2
from ui.paginas.facturas.nota_credito.nueva.paso3_confirmacion import construir_paso3

_NOMBRES_PASO = {
    1: "Motivo",
    2: "Líneas",
    3: "Confirmación",
}


def _es_elegible(factura: FacturaDetalle) -> bool:
    return factura.estado == "ACEPTADO" and factura.tipo_comprobante == "01"


def vista_facturas_nota_credito_nueva(page: ft.Page) -> ft.View:
    id_factura_origen = router_query.parametro(page.route, "factura_id")

    texto_estado = ft.Text("Cargando...", theme_style=ft.TextThemeStyle.BODY_SMALL)
    texto_error = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    indicador_paso = ft.Text(
        theme_style=ft.TextThemeStyle.BODY_SMALL, color=tokens.GRAFITO, visible=False
    )
    contenedor_paso = ft.Column()

    async def cargar() -> None:
        if not id_factura_origen:
            texto_estado.visible = False
            texto_error.value = "Factura origen no especificada."
            texto_error.visible = True
            page.update()
            return

        try:
            resultado = await obtener_factura(id_factura_origen)
        except SesionExpirada:
            page.navigate(rutas.LOGIN)
            return

        texto_estado.visible = False

        if isinstance(resultado, ApiFallo):
            texto_error.value = resultado.error.mensaje
            texto_error.visible = True
            page.update()
            return

        factura = resultado.datos
        if factura is None:
            texto_error.value = "Factura no encontrada."
            texto_error.visible = True
            page.update()
            return

        if not _es_elegible(factura):
            texto_error.value = (
                "Solo se puede emitir una nota de crédito sobre una factura electrónica "
                "(tipo 01) que esté en estado ACEPTADO."
            )
            texto_error.visible = True
            page.update()
            return

        estado = EstadoNotaCredito(
            factura_origen_id=factura.id,
            factura_origen_consecutivo=factura.consecutivo,
            cliente_nombre=factura.cliente_nombre,
            lineas=lineas_seleccionables_desde_factura(factura.lineas),
            moneda=factura.moneda,
        )

        def ir_a_paso(numero: int) -> None:
            estado.paso = numero
            renderizar_paso()

        def renderizar_paso() -> None:
            indicador_paso.value = f"Paso {estado.paso} de 3 — {_NOMBRES_PASO[estado.paso]}"
            if estado.paso == 1:
                contenedor_paso.controls = [construir_paso1(page, estado, ir_a_paso)]
            elif estado.paso == 2:
                contenedor_paso.controls = [construir_paso2(page, estado, ir_a_paso)]
            else:
                contenedor_paso.controls = [construir_paso3(page, estado, ir_a_paso)]
            page.update()

        indicador_paso.visible = True
        renderizar_paso()

    page.run_task(cargar)

    contenido_pagina = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(
                        "Nueva nota de crédito", theme_style=ft.TextThemeStyle.HEADLINE_LARGE
                    ),
                    ft.TextButton(
                        content="Cancelar",
                        on_click=lambda e: page.navigate(
                            rutas.FACTURAS_DETALLE, id=id_factura_origen or ""
                        ),
                    ),
                ],
            ),
            texto_estado,
            texto_error,
            indicador_paso,
            contenedor_paso,
        ],
    )

    return construir_vista_protegida(
        page, rutas.FACTURAS_NOTA_CREDITO_NUEVA, rutas.FACTURAS, contenido_pagina
    )
