import base64

import flet as ft

import estado_navegacion
import rutas
from api import sesion
from api.cliente import ApiFallo
from api.mfa import confirmar_enrolamiento, iniciar_enrolamiento
from diseno import tokens
from ui.componentes.contenedor_responsivo import contenedor_ancho_limitado


def vista_mfa_enrolar(page: ft.Page) -> ft.View:
    token = estado_navegacion.obtener_token_mfa_pendiente()

    texto_estado = ft.Text(
        "Generando código QR...", theme_style=ft.TextThemeStyle.BODY_SMALL
    )
    contenedor_qr = ft.Container(visible=False)
    texto_secreto = ft.Text(
        value="",
        theme_style=ft.TextThemeStyle.BODY_SMALL,
        font_family=tokens.FUENTE_MONO,
        visible=False,
        selectable=True,
    )

    campo_codigo = ft.TextField(
        label="Código de verificación",
        hint_text="123456",
        max_length=6,
        keyboard_type=ft.KeyboardType.NUMBER,
        text_align=ft.TextAlign.CENTER,
    )
    texto_error = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    boton_confirmar = ft.Button(content="Confirmar")
    boton_cancelar = ft.TextButton(content="Cancelar")

    def mostrar_error(mensaje: str) -> None:
        texto_error.value = mensaje
        texto_error.visible = True
        page.update()

    async def cargar_enrolamiento() -> None:
        resultado = await iniciar_enrolamiento(token)
        if isinstance(resultado, ApiFallo):
            texto_estado.value = ""
            mostrar_error(resultado.error.mensaje)
            return

        datos = resultado.datos
        texto_estado.visible = False
        if datos.qr_code_base64_png:
            contenedor_qr.content = ft.Image(
                src=base64.b64decode(datos.qr_code_base64_png),
                width=220,
                height=220,
            )
            contenedor_qr.visible = True
        if datos.secreto_base32:
            texto_secreto.value = (
                f"Si no podés escanear el QR, ingresá este código manualmente: "
                f"{datos.secreto_base32}"
            )
            texto_secreto.visible = True
        page.update()

    async def al_confirmar(e: ft.Event[ft.Button]) -> None:
        codigo = campo_codigo.value.strip()
        if not token:
            page.navigate(rutas.LOGIN)
            return
        if len(codigo) != 6 or not codigo.isdigit():
            mostrar_error("El código debe ser de 6 dígitos.")
            return

        texto_error.visible = False
        boton_confirmar.disabled = True
        boton_confirmar.content = "Confirmando..."
        page.update()

        resultado = await confirmar_enrolamiento(token, codigo)

        boton_confirmar.disabled = False
        boton_confirmar.content = "Confirmar"

        if isinstance(resultado, ApiFallo):
            mostrar_error(resultado.error.mensaje)
            return

        estado_navegacion.limpiar()
        caso = resultado.datos
        await sesion.guardar_tokens(caso.access_token, caso.refresh_token)
        await sesion.guardar_empresa_activa(caso.empresa_id)
        page.navigate(rutas.DASHBOARD)

    def al_cancelar(e: ft.Event[ft.TextButton]) -> None:
        estado_navegacion.limpiar()
        page.navigate(rutas.LOGIN)

    boton_confirmar.on_click = al_confirmar
    boton_cancelar.on_click = al_cancelar
    campo_codigo.on_submit = al_confirmar

    if not token:
        page.navigate(rutas.LOGIN)
    else:
        page.run_task(cargar_enrolamiento)

    formulario = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=16,
        controls=[
            ft.Text(
                "Configurar verificación en dos pasos",
                theme_style=ft.TextThemeStyle.HEADLINE_LARGE,
            ),
            ft.Text(
                "Escaneá el código QR con tu aplicación autenticadora "
                "(Google Authenticator, Authy, etc.) y luego ingresá "
                "el código de 6 dígitos que te muestre.",
                theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                color=tokens.GRAFITO,
                text_align=ft.TextAlign.CENTER,
            ),
            texto_estado,
            contenedor_qr,
            texto_secreto,
            campo_codigo,
            texto_error,
            boton_confirmar,
            boton_cancelar,
        ],
    )

    return ft.View(
        route=rutas.MFA_ENROLAR,
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.Container(
                    alignment=ft.Alignment.CENTER,
                    padding=24,
                    content=contenedor_ancho_limitado(
                        page, formulario, tokens.ANCHO_FORMULARIO_AUTH
                    ),
                ),
            )
        ],
    )
