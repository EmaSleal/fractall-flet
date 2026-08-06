import flet as ft

import rutas
import validacion
from api.cliente import ApiFallo
from api.verificacion import reenviar_verificacion, verificar_email
from diseno import tokens
from ui.componentes.contenedor_responsivo import contenedor_ancho_limitado


def vista_verificar_email(page: ft.Page) -> ft.View:
    campo_token = ft.TextField(
        label="Código recibido por correo",
        hint_text="Pegá acá el código del correo",
        autofocus=True,
    )
    texto_error = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    boton_verificar = ft.Button(content="Verificar correo")

    campo_email_reenvio = ft.TextField(
        label="Correo electrónico", keyboard_type=ft.KeyboardType.EMAIL
    )
    texto_reenvio = ft.Text(value="", visible=False, color=tokens.GRAFITO)
    boton_reenviar = ft.TextButton(content="Reenviar código")

    def mostrar_error(mensaje: str) -> None:
        texto_error.value = mensaje
        texto_error.visible = True
        page.update()

    def mostrar_mensaje_reenvio(mensaje: str) -> None:
        texto_reenvio.value = mensaje
        texto_reenvio.visible = True
        page.update()

    def vista_exito() -> ft.View:
        contenido_exito = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            controls=[
                ft.Text(
                    "Correo verificado", theme_style=ft.TextThemeStyle.HEADLINE_LARGE
                ),
                ft.Text(
                    "Ya podés iniciar sesión con tu cuenta.",
                    theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                    color=tokens.GRAFITO,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Button(
                    content="Ir a iniciar sesión",
                    on_click=lambda e: page.navigate(rutas.LOGIN),
                ),
            ],
        )
        return ft.View(
            route=rutas.VERIFICAR_EMAIL,
            controls=[
                ft.SafeArea(
                    expand=True,
                    content=ft.Container(
                        alignment=ft.Alignment.CENTER,
                        padding=24,
                        content=contenedor_ancho_limitado(
                            page, contenido_exito, tokens.ANCHO_FORMULARIO_AUTH
                        ),
                    ),
                )
            ],
        )

    async def al_verificar(e: ft.Event[ft.Button]) -> None:
        token = campo_token.value.strip()
        if not token:
            mostrar_error("Pegá el código que recibiste por correo.")
            return

        texto_error.visible = False
        boton_verificar.disabled = True
        boton_verificar.content = "Verificando..."
        page.update()

        resultado = await verificar_email(token)

        boton_verificar.disabled = False
        boton_verificar.content = "Verificar correo"

        if isinstance(resultado, ApiFallo):
            mostrar_error(resultado.error.mensaje)
            return

        page.views[-1] = vista_exito()
        page.update()

    async def al_reenviar(e: ft.Event[ft.TextButton]) -> None:
        email = campo_email_reenvio.value.strip()
        if not validacion.email_valido(email):
            mostrar_mensaje_reenvio("Ingresá un correo electrónico válido.")
            return

        boton_reenviar.disabled = True
        page.update()

        resultado = await reenviar_verificacion(email)

        boton_reenviar.disabled = False

        if isinstance(resultado, ApiFallo):
            mostrar_mensaje_reenvio(resultado.error.mensaje)
            return

        mostrar_mensaje_reenvio("Si el correo está registrado, te reenviamos el código.")

    boton_verificar.on_click = al_verificar
    boton_reenviar.on_click = al_reenviar
    campo_token.on_submit = al_verificar
    campo_email_reenvio.on_submit = al_reenviar

    formulario = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        controls=[
            ft.Text("Verificar correo", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
            ft.Text(
                "Pegá el código que recibiste por correo para activar tu cuenta.",
                theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                color=tokens.GRAFITO,
            ),
            campo_token,
            texto_error,
            boton_verificar,
            ft.Divider(),
            ft.Text(
                "¿No te llegó el código?",
                theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
            ),
            campo_email_reenvio,
            texto_reenvio,
            boton_reenviar,
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.TextButton(
                        content="Volver a iniciar sesión",
                        on_click=lambda e: page.navigate(rutas.LOGIN),
                    ),
                ],
            ),
        ],
    )

    return ft.View(
        route=rutas.VERIFICAR_EMAIL,
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
