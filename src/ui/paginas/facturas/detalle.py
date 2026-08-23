import flet as ft

import catalogos
import formato
import polling_estado
import router_query
import rutas
from api.cliente import ApiFallo
from api.cliente_autenticado import SesionExpirada
from api.facturas import (
    FacturaDetalle,
    descargar_pdf,
    descargar_xml_factura,
    descargar_xml_respuesta,
    obtener_factura,
    reenviar_factura,
)
from api.perfil import obtener_perfil
from diseno import tokens
from ui.componentes.sello_estado import construir_sello_estado
from ui.componentes.shell_protegido import construir_vista_protegida


def _puede_reenviar(factura: FacturaDetalle) -> bool:
    return (
        factura.estado == "ENVIADO"
        and factura.ultimo_resultado_consulta == "ERROR_COMUNICACION"
    )


def vista_facturas_detalle(page: ft.Page) -> ft.View:
    id_factura = router_query.parametro(page.route, "id")

    texto_estado = ft.Text("Cargando...", theme_style=ft.TextThemeStyle.BODY_SMALL)
    texto_error = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    contenedor_encabezado = ft.Column(visible=False)
    contenedor_contenido = ft.Column(visible=False, spacing=20)

    selector_archivo = ft.FilePicker()
    portapapeles = ft.Clipboard()

    async def cargar() -> None:
        if not id_factura:
            texto_estado.visible = False
            texto_error.value = "Factura no especificada."
            texto_error.visible = True
            page.update()
            return

        try:
            resultado_factura = await obtener_factura(id_factura)
            resultado_perfil = await obtener_perfil()
        except SesionExpirada:
            page.navigate(rutas.LOGIN)
            return

        texto_estado.visible = False

        if isinstance(resultado_factura, ApiFallo):
            texto_error.value = resultado_factura.error.mensaje
            texto_error.visible = True
            page.update()
            return

        factura = resultado_factura.datos
        if factura is None:
            texto_error.value = "Factura no encontrada."
            texto_error.visible = True
            page.update()
            return

        permisos = (
            []
            if isinstance(resultado_perfil, ApiFallo)
            else resultado_perfil.datos.permisos
        )
        tiene_permiso_reenviar = "factura.reenviar" in permisos
        _armar_contenido(factura, tiene_permiso_reenviar)

        factura_final = await polling_estado.esperar_estado_final(
            consultar=lambda: obtener_factura(id_factura),
            estado_inicial=factura.estado,
            extraer_estado=lambda f: f.estado,
        )
        if factura_final is not None:
            _armar_contenido(factura_final, tiene_permiso_reenviar)

    def _armar_contenido(factura: FacturaDetalle, tiene_permiso_reenviar: bool) -> None:
        contenedor_encabezado.controls = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                catalogos.label_tipo_comprobante(factura.tipo_comprobante)
                                if factura.tipo_comprobante
                                else "Factura electrónica",
                                theme_style=ft.TextThemeStyle.BODY_SMALL,
                                color=tokens.GRAFITO,
                            ),
                            ft.Text(
                                factura.consecutivo,
                                theme_style=ft.TextThemeStyle.HEADLINE_LARGE,
                                font_family=tokens.FUENTE_MONO,
                            ),
                            ft.Text(
                                factura.cliente_nombre,
                                theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                            ),
                        ],
                    ),
                    construir_sello_estado(factura.estado, tamano_icono=20),
                ],
            )
        ]
        contenedor_encabezado.visible = True

        bloques: list[ft.Control] = []

        es_error_comunicacion = factura.ultimo_resultado_consulta == "ERROR_COMUNICACION"
        es_rechazado = factura.estado == "RECHAZADO"
        if es_error_comunicacion or es_rechazado:
            controles_aviso = []
            if factura.codigo_respuesta:
                controles_aviso.append(
                    ft.Text(
                        f"Código: {factura.codigo_respuesta}",
                        theme_style=ft.TextThemeStyle.BODY_SMALL,
                        font_family=tokens.FUENTE_MONO,
                    )
                )
            if factura.mensaje_respuesta:
                controles_aviso.append(
                    ft.Text(factura.mensaje_respuesta, theme_style=ft.TextThemeStyle.BODY_MEDIUM)
                )
            if es_error_comunicacion:
                controles_aviso.append(
                    ft.Text(
                        "Use el botón Reenviar factura para intentar de nuevo.",
                        theme_style=ft.TextThemeStyle.BODY_SMALL,
                        color=tokens.GRAFITO,
                    )
                )
            bloques.append(
                ft.Container(
                    padding=16,
                    border=ft.Border.all(1, tokens.ESTADO_RECHAZADO),
                    border_radius=tokens.RADIO_LG,
                    content=ft.Column(spacing=4, controls=controles_aviso),
                )
            )

        bloques.append(
            ft.ResponsiveRow(
                controls=[
                    ft.Column(
                        col={"xs": 12, "sm": 6},
                        spacing=4,
                        controls=[
                            ft.Text("Metadatos", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        f"Clave: {factura.clave_numerica}",
                                        theme_style=ft.TextThemeStyle.BODY_SMALL,
                                        font_family=tokens.FUENTE_MONO,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.CONTENT_COPY,
                                        icon_size=14,
                                        on_click=lambda e: page.run_task(
                                            portapapeles.set, factura.clave_numerica
                                        ),
                                    ),
                                ]
                            ),
                            ft.Text(
                                f"Ambiente: {factura.ambiente_hacienda}",
                                theme_style=ft.TextThemeStyle.BODY_SMALL,
                            ),
                            ft.Text(
                                f"Emitida: {formato.formatear_fecha(factura.fecha_emision)}",
                                theme_style=ft.TextThemeStyle.BODY_SMALL,
                            ),
                        ]
                        + (
                            [
                                ft.Text(
                                    f"Respondida: {formato.formatear_fecha(factura.fecha_respuesta)}",
                                    theme_style=ft.TextThemeStyle.BODY_SMALL,
                                )
                            ]
                            if factura.fecha_respuesta
                            else []
                        ),
                    ),
                    ft.Column(
                        col={"xs": 12, "sm": 6},
                        spacing=4,
                        controls=[
                            ft.Text("Totales", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                            ft.Text(
                                f"Subtotal: {formato.formatear_moneda(factura.subtotal, factura.moneda)}",
                                theme_style=ft.TextThemeStyle.BODY_SMALL,
                                font_family=tokens.FUENTE_MONO,
                            ),
                            ft.Text(
                                f"IVA: {formato.formatear_moneda(factura.total_impuesto, factura.moneda)}",
                                theme_style=ft.TextThemeStyle.BODY_SMALL,
                                font_family=tokens.FUENTE_MONO,
                            ),
                            ft.Text(
                                f"Total: {formato.formatear_moneda(factura.total, factura.moneda)}",
                                theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                                font_family=tokens.FUENTE_MONO,
                            ),
                        ],
                    ),
                ]
            )
        )

        if factura.lineas:
            filas_lineas = [
                ft.Container(
                    border=ft.Border.all(1, tokens.ARENA),
                    border_radius=tokens.RADIO_MD,
                    padding=12,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                f"#{linea.numero_linea} · CABYS "
                                f"{linea.codigo_cabys_aplicado or '—'}"
                                + (" · Exonerada" if linea.exoneracion_id else ""),
                                theme_style=ft.TextThemeStyle.BODY_SMALL,
                            ),
                            ft.Text(
                                f"{linea.cantidad} × "
                                f"{formato.formatear_moneda(linea.precio_unitario, factura.moneda)} "
                                f"({linea.porcentaje_impuesto_aplicado}%) = "
                                f"{formato.formatear_moneda(linea.subtotal, factura.moneda)}",
                                theme_style=ft.TextThemeStyle.BODY_SMALL,
                                font_family=tokens.FUENTE_MONO,
                            ),
                        ],
                    ),
                )
                for linea in factura.lineas
            ]
            bloques.append(
                ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text("Líneas", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                        *filas_lineas,
                    ],
                )
            )

        if factura.medios_pago:
            bloques.append(
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text("Medios de pago", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                        *[
                            ft.Text(
                                f"{m.medio_pago_otros or catalogos.label_tipo_medio_pago(m.tipo_medio_pago)}: "
                                f"{formato.formatear_moneda(m.total_medio_pago, factura.moneda)}",
                                theme_style=ft.TextThemeStyle.BODY_SMALL,
                                font_family=tokens.FUENTE_MONO,
                            )
                            for m in factura.medios_pago
                        ],
                    ],
                )
            )

        if factura.otros_cargos:
            bloques.append(
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text("Otros cargos", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                        *[
                            ft.Text(
                                f"{c.detalle or c.nombre_tercero or 'Cargo'}: "
                                f"{formato.formatear_moneda(c.monto_cargo, factura.moneda)}",
                                theme_style=ft.TextThemeStyle.BODY_SMALL,
                                font_family=tokens.FUENTE_MONO,
                            )
                            for c in factura.otros_cargos
                        ],
                    ],
                )
            )

        async def descargar(
            nombre_por_defecto: str, funcion_descarga
        ) -> None:
            resultado = await funcion_descarga(factura.id)
            if isinstance(resultado, ApiFallo):
                texto_error.value = resultado.error.mensaje
                texto_error.visible = True
                page.update()
                return
            archivo = resultado.datos
            await selector_archivo.save_file(
                file_name=archivo.nombre_archivo or nombre_por_defecto,
                src_bytes=archivo.contenido,
            )

        botones_acciones = [
            ft.Button(
                content="Descargar PDF",
                on_click=lambda e: page.run_task(
                    descargar, f"{factura.consecutivo}.pdf", descargar_pdf
                ),
            ),
            ft.Button(
                content="Descargar XML",
                on_click=lambda e: page.run_task(
                    descargar, f"{factura.consecutivo}.xml", descargar_xml_factura
                ),
            ),
        ]
        if factura.comprobante_id and factura.estado in (
            "ENVIADO",
            "ACEPTADO",
            "RECHAZADO",
        ):
            botones_acciones.append(
                ft.Button(
                    content="Descargar respuesta Hacienda",
                    on_click=lambda e: page.run_task(
                        descargar,
                        f"{factura.consecutivo}-respuesta.xml",
                        descargar_xml_respuesta,
                    ),
                )
            )

        if tiene_permiso_reenviar and _puede_reenviar(factura):
            boton_reenviar = ft.Button(content="Reenviar factura")

            async def al_reenviar(e: ft.Event[ft.Button]) -> None:
                boton_reenviar.disabled = True
                boton_reenviar.content = "Reenviando..."
                page.update()

                resultado = await reenviar_factura(factura.id)

                if isinstance(resultado, ApiFallo):
                    boton_reenviar.disabled = False
                    boton_reenviar.content = "Reenviar factura"
                    texto_error.value = resultado.error.mensaje
                    texto_error.visible = True
                    page.update()
                    return

                await cargar()

            boton_reenviar.on_click = al_reenviar
            botones_acciones.append(boton_reenviar)

        bloques.append(ft.Row(wrap=True, spacing=8, controls=botones_acciones))

        contenedor_contenido.controls = bloques
        contenedor_contenido.visible = True
        page.update()

    page.run_task(cargar)

    contenido_pagina = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.TextButton(
                content="← Facturas", on_click=lambda e: page.navigate(rutas.FACTURAS)
            ),
            texto_estado,
            texto_error,
            contenedor_encabezado,
            contenedor_contenido,
        ],
    )

    return construir_vista_protegida(page, rutas.FACTURAS_DETALLE, rutas.FACTURAS, contenido_pagina)
