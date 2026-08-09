import flet as ft

import catalogos
import rutas
from api.cliente import ApiFallo
from api.cliente_autenticado import SesionExpirada
from api.empresa import (
    DatosFiscales,
    Empresa,
    actualizar_datos_fiscales,
    cambiar_ambiente,
    cargar_certificado,
    configurar_credenciales_hacienda,
    obtener_empresa,
)
from diseno import tokens
from ui.componentes.badge import construir_badge
from ui.componentes.bloque_ubicacion import construir_bloque_ubicacion
from ui.componentes.shell_protegido import construir_vista_protegida

_COLOR_POR_CATEGORIA = {
    "aceptado": tokens.ESTADO_ACEPTADO,
    "pendiente": tokens.ESTADO_PENDIENTE,
    "rechazado": tokens.ESTADO_RECHAZADO,
    "neutral": tokens.GRAFITO,
}


def _badge_estado(status: str) -> ft.Container:
    etiqueta, categoria = catalogos.info_estado_empresa(status)
    return construir_badge(etiqueta, _COLOR_POR_CATEGORIA[categoria])


def vista_empresa(page: ft.Page) -> ft.View:
    texto_estado = ft.Text("Cargando...", theme_style=ft.TextThemeStyle.BODY_SMALL)
    texto_error = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    contenedor_encabezado = ft.Row(visible=False)
    contenedor_secciones = ft.Column(visible=False, spacing=24)

    # --- sección datos fiscales ---
    campo_razon_social = ft.TextField(label="Razón social", max_length=255)
    campo_nombre_comercial = ft.TextField(label="Nombre comercial", max_length=255)
    campo_numero_identificacion = ft.TextField(
        label="Número de identificación", max_length=20
    )
    campo_tipo_identificacion = ft.Dropdown(
        label="Tipo de identificación",
        options=[
            ft.DropdownOption(key=clave, text=f"{clave} — {etiqueta}")
            for clave, etiqueta in catalogos.TIPOS_IDENTIFICACION
        ],
    )
    campo_codigo_actividad = ft.TextField(label="Código de actividad", max_length=6)
    bloque_ubicacion = construir_bloque_ubicacion(page, col={"xs": 12, "sm": 6})
    campo_provincia = bloque_ubicacion.provincia
    campo_canton = bloque_ubicacion.canton
    campo_distrito = bloque_ubicacion.distrito
    campo_barrio = ft.TextField(label="Barrio", max_length=100, col={"xs": 12, "sm": 6})
    campo_otras_senas = ft.TextField(
        label="Otras señas", max_length=300, multiline=True, max_lines=2
    )
    campo_telefono = ft.TextField(label="Teléfono", max_length=20)
    campo_email = ft.TextField(
        label="Correo electrónico", max_length=255, keyboard_type=ft.KeyboardType.EMAIL
    )
    texto_error_fiscales = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    boton_guardar_fiscales = ft.Button(content="Guardar datos fiscales")

    # --- sección ambiente (única fuente de verdad, compartida con credenciales) ---
    campo_ambiente = ft.Dropdown(
        label="Ambiente de Hacienda",
        value="SANDBOX",
        options=[
            ft.DropdownOption(key=clave, text=etiqueta)
            for clave, etiqueta in catalogos.AMBIENTES_HACIENDA
        ],
    )
    texto_error_ambiente = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    boton_guardar_ambiente = ft.Button(content="Guardar ambiente")

    # --- sección credenciales Hacienda ---
    campo_usuario_hacienda = ft.TextField(label="Usuario de Hacienda", max_length=255)
    campo_password_hacienda = ft.TextField(
        label="Contraseña de Hacienda", password=True, can_reveal_password=True
    )
    texto_error_credenciales = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    boton_guardar_credenciales = ft.Button(content="Guardar credenciales")

    # --- sección certificado ---
    selector_archivo = ft.FilePicker()
    texto_archivo_elegido = ft.Text(
        "Ningún archivo seleccionado", theme_style=ft.TextThemeStyle.BODY_SMALL
    )
    campo_pin = ft.TextField(label="PIN del certificado", password=True, can_reveal_password=True)
    texto_error_certificado = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    boton_subir_certificado = ft.Button(content="Subir certificado", disabled=True)
    texto_estado_certificado = ft.Text(theme_style=ft.TextThemeStyle.BODY_SMALL)

    archivo_elegido: dict = {"nombre": None, "bytes": None}

    async def al_elegir_archivo(e: ft.Event[ft.FilePicker]) -> None:
        archivos = await selector_archivo.pick_files(
            dialog_title="Elegir certificado (.p12)",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["p12"],
            with_data=True,
        )
        if not archivos:
            return
        archivo = archivos[0]
        archivo_elegido["nombre"] = archivo.name
        archivo_elegido["bytes"] = archivo.bytes
        texto_archivo_elegido.value = archivo.name
        boton_subir_certificado.disabled = False
        page.update()

    boton_elegir_archivo = ft.Button(
        content="Elegir archivo .p12", on_click=al_elegir_archivo
    )

    async def cargar() -> None:
        try:
            resultado = await obtener_empresa()
        except SesionExpirada:
            page.navigate(rutas.LOGIN)
            return

        texto_estado.visible = False

        if isinstance(resultado, ApiFallo):
            texto_error.value = resultado.error.mensaje
            texto_error.visible = True
            page.update()
            return

        aplicar_empresa(resultado.datos)

    def aplicar_empresa(empresa: Empresa) -> None:
        campo_razon_social.value = empresa.razon_social or ""
        campo_nombre_comercial.value = empresa.nombre_comercial or ""
        campo_numero_identificacion.value = empresa.numero_identificacion or ""
        campo_tipo_identificacion.value = empresa.tipo_identificacion
        campo_codigo_actividad.value = empresa.codigo_actividad or ""
        campo_provincia.value = empresa.codigo_provincia or None
        campo_canton.value = empresa.canton or None
        campo_distrito.value = empresa.distrito or None
        page.run_task(bloque_ubicacion.sincronizar_cascada)
        campo_barrio.value = empresa.barrio or ""
        campo_otras_senas.value = empresa.otras_senas or ""
        campo_telefono.value = empresa.telefono or ""
        campo_email.value = empresa.email or ""
        campo_ambiente.value = empresa.ambiente_hacienda or "SANDBOX"
        texto_estado_certificado.value = (
            "✓ Certificado cargado" if empresa.tiene_certificado else "Sin certificado cargado"
        )
        texto_estado_certificado.color = (
            tokens.ESTADO_ACEPTADO if empresa.tiene_certificado else tokens.GRAFITO
        )

        contenedor_encabezado.controls = [
            ft.Text("Empresa", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
            _badge_estado(empresa.status),
        ]
        contenedor_encabezado.visible = True

        oculto = empresa.status in catalogos.ESTADOS_ADMINISTRATIVOS
        secciones = [_seccion_datos_fiscales()]
        if not oculto:
            secciones.append(_seccion_ambiente())
            secciones.append(_seccion_credenciales())
            secciones.append(_seccion_certificado())
        contenedor_secciones.controls = secciones
        contenedor_secciones.visible = True
        page.update()

    async def al_guardar_fiscales(e: ft.Event[ft.Button]) -> None:
        texto_error_fiscales.visible = False
        boton_guardar_fiscales.disabled = True
        boton_guardar_fiscales.content = "Guardando..."
        page.update()

        datos = DatosFiscales(
            razon_social=campo_razon_social.value,
            nombre_comercial=campo_nombre_comercial.value,
            numero_identificacion=campo_numero_identificacion.value,
            tipo_identificacion=campo_tipo_identificacion.value or "",
            codigo_actividad=campo_codigo_actividad.value,
            codigo_provincia=campo_provincia.value or "",
            canton=campo_canton.value or "",
            distrito=campo_distrito.value or "",
            barrio=campo_barrio.value,
            otras_senas=campo_otras_senas.value,
            telefono=campo_telefono.value,
            email=campo_email.value,
        )
        resultado = await actualizar_datos_fiscales(datos)

        boton_guardar_fiscales.disabled = False
        boton_guardar_fiscales.content = "Guardar datos fiscales"

        if isinstance(resultado, ApiFallo):
            texto_error_fiscales.value = resultado.error.mensaje
            texto_error_fiscales.visible = True
            page.update()
            return

        aplicar_empresa(resultado.datos)

    boton_guardar_fiscales.on_click = al_guardar_fiscales
    # campo_otras_senas queda afuera: es multilinea, Enter ahí inserta un
    # salto de línea en vez de enviar el formulario. provincia/canton/distrito
    # quedan afuera también: son Dropdown, no tienen on_submit.
    for campo in (
        campo_razon_social,
        campo_nombre_comercial,
        campo_numero_identificacion,
        campo_codigo_actividad,
        campo_barrio,
        campo_telefono,
        campo_email,
    ):
        campo.on_submit = al_guardar_fiscales

    async def al_guardar_ambiente(e: ft.Event[ft.Button]) -> None:
        texto_error_ambiente.visible = False
        boton_guardar_ambiente.disabled = True
        page.update()

        resultado = await cambiar_ambiente(campo_ambiente.value)

        boton_guardar_ambiente.disabled = False

        if isinstance(resultado, ApiFallo):
            texto_error_ambiente.value = resultado.error.mensaje
            texto_error_ambiente.visible = True
        page.update()

    boton_guardar_ambiente.on_click = al_guardar_ambiente

    async def al_guardar_credenciales(e: ft.Event[ft.Button]) -> None:
        texto_error_credenciales.visible = False

        if not campo_usuario_hacienda.value.strip() or not campo_password_hacienda.value:
            texto_error_credenciales.value = "Usuario y contraseña son obligatorios."
            texto_error_credenciales.visible = True
            page.update()
            return

        boton_guardar_credenciales.disabled = True
        boton_guardar_credenciales.content = "Guardando..."
        page.update()

        resultado = await configurar_credenciales_hacienda(
            campo_usuario_hacienda.value, campo_password_hacienda.value, campo_ambiente.value
        )

        boton_guardar_credenciales.disabled = False
        boton_guardar_credenciales.content = "Guardar credenciales"

        if isinstance(resultado, ApiFallo):
            texto_error_credenciales.value = resultado.error.mensaje
            texto_error_credenciales.visible = True
            page.update()
            return

        campo_password_hacienda.value = ""
        await cargar()

    boton_guardar_credenciales.on_click = al_guardar_credenciales
    campo_usuario_hacienda.on_submit = al_guardar_credenciales
    campo_password_hacienda.on_submit = al_guardar_credenciales

    async def al_subir_certificado(e: ft.Event[ft.Button]) -> None:
        texto_error_certificado.visible = False

        if not archivo_elegido["bytes"]:
            texto_error_certificado.value = "Elegí un archivo .p12 primero."
            texto_error_certificado.visible = True
            page.update()
            return
        if not campo_pin.value:
            texto_error_certificado.value = "El PIN es obligatorio."
            texto_error_certificado.visible = True
            page.update()
            return

        boton_subir_certificado.disabled = True
        boton_subir_certificado.content = "Subiendo..."
        page.update()

        resultado = await cargar_certificado(
            archivo_elegido["nombre"], archivo_elegido["bytes"], campo_pin.value
        )

        boton_subir_certificado.disabled = False
        boton_subir_certificado.content = "Subir certificado"

        if isinstance(resultado, ApiFallo):
            texto_error_certificado.value = resultado.error.mensaje
            texto_error_certificado.visible = True
            page.update()
            return

        campo_pin.value = ""
        archivo_elegido["nombre"] = None
        archivo_elegido["bytes"] = None
        texto_archivo_elegido.value = "Ningún archivo seleccionado"
        boton_subir_certificado.disabled = True
        await cargar()

    boton_subir_certificado.on_click = al_subir_certificado
    campo_pin.on_submit = al_subir_certificado

    def _seccion_datos_fiscales() -> ft.Column:
        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=12,
            controls=[
                ft.Text("Datos fiscales", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                campo_razon_social,
                campo_nombre_comercial,
                campo_numero_identificacion,
                campo_tipo_identificacion,
                campo_codigo_actividad,
                ft.ResponsiveRow(
                    controls=[campo_provincia, campo_canton, campo_distrito, campo_barrio]
                ),
                campo_otras_senas,
                campo_telefono,
                campo_email,
                texto_error_fiscales,
                boton_guardar_fiscales,
            ],
        )

    def _seccion_ambiente() -> ft.Column:
        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=12,
            controls=[
                ft.Text("Ambiente de Hacienda", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Text(
                    "Esta versión opera únicamente en SANDBOX — PRODUCCION está "
                    "disponible en el backend pero no se recomienda usarla todavía.",
                    theme_style=ft.TextThemeStyle.BODY_SMALL,
                    color=tokens.GRAFITO,
                ),
                campo_ambiente,
                texto_error_ambiente,
                boton_guardar_ambiente,
            ],
        )

    def _seccion_credenciales() -> ft.Column:
        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=12,
            controls=[
                ft.Text(
                    "Credenciales de Hacienda", theme_style=ft.TextThemeStyle.TITLE_MEDIUM
                ),
                ft.Text(
                    "Se guardan para el ambiente seleccionado arriba.",
                    theme_style=ft.TextThemeStyle.BODY_SMALL,
                    color=tokens.GRAFITO,
                ),
                campo_usuario_hacienda,
                campo_password_hacienda,
                texto_error_credenciales,
                boton_guardar_credenciales,
            ],
        )

    def _seccion_certificado() -> ft.Column:
        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=12,
            controls=[
                ft.Text("Certificado de firma", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                texto_estado_certificado,
                ft.Row(controls=[boton_elegir_archivo, texto_archivo_elegido]),
                campo_pin,
                texto_error_certificado,
                boton_subir_certificado,
            ],
        )

    page.run_task(bloque_ubicacion.cargar_provincias)
    page.run_task(cargar)

    contenido_pagina = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            contenedor_encabezado,
            texto_estado,
            texto_error,
            contenedor_secciones,
        ],
    )

    return construir_vista_protegida(page, rutas.EMPRESA, rutas.EMPRESA, contenido_pagina)
