import flet as ft

import rutas
import validacion
from api.auth import restablecer_password
from api.cliente import ApiFallo
from diseno import tokens
from ui.componentes.contenedor_responsivo import contenedor_ancho_limitado


def vista_restablecer_password(page: ft.Page) -> ft.View:
    campo_token = ft.TextField(
        label="Código recibido por correo",
        hint_text="Pegá acá el código del correo",
        autofocus=True,
    )
    campo_password = ft.TextField(
        label="Nueva contraseña",
        password=True,
        can_reveal_password=True,
        max_length=72,
        autofill_hints=[ft.AutofillHint.NEW_PASSWORD],
    )
    campo_confirmar = ft.TextField(
        label="Confirmar nueva contraseña",
        password=True,
        can_reveal_password=True,
        max_length=72,
        autofill_hints=[ft.AutofillHint.NEW_PASSWORD],
    )
    texto_error = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    boton_restablecer = ft.Button(content="Restablecer contraseña")

    def mostrar_error(mensaje: str) -> None:
        texto_error.value = mensaje
        texto_error.visible = True
        page.update()

    def vista_exito() -> ft.View:
        contenido_exito = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            controls=[
                ft.Text(
                    "Contraseña actualizada",
                    theme_style=ft.TextThemeStyle.HEADLINE_LARGE,
                ),
                ft.Text(
                    "Ya podés iniciar sesión con tu nueva contraseña.",
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
            route=rutas.RESTABLECER_PASSWORD,
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

    async def al_enviar(e: ft.Event[ft.Button]) -> None:
        token = campo_token.value.strip()
        password = campo_password.value
        confirmar = campo_confirmar.value

        if not token:
            mostrar_error("Pegá el código que recibiste por correo.")
            return
        if not validacion.password_valida(password):
            mostrar_error("La contraseña no cumple los requisitos mínimos.")
            return
        if password != confirmar:
            mostrar_error("Las contraseñas no coinciden.")
            return

        texto_error.visible = False
        boton_restablecer.disabled = True
        boton_restablecer.content = "Restableciendo..."
        page.update()

        resultado = await restablecer_password(token, password)

        boton_restablecer.disabled = False
        boton_restablecer.content = "Restablecer contraseña"

        if isinstance(resultado, ApiFallo):
            mostrar_error(resultado.error.mensaje)
            return

        page.views[-1] = vista_exito()
        page.update()

    boton_restablecer.on_click = al_enviar
    campo_token.on_submit = al_enviar
    campo_password.on_submit = al_enviar
    campo_confirmar.on_submit = al_enviar

    formulario = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        controls=[
            ft.Text(
                "Restablecer contraseña", theme_style=ft.TextThemeStyle.HEADLINE_LARGE
            ),
            ft.Text(
                "Pegá el código que recibiste por correo y elegí una "
                "contraseña nueva.",
                theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                color=tokens.GRAFITO,
            ),
            campo_token,
            campo_password,
            campo_confirmar,
            texto_error,
            boton_restablecer,
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
        route=rutas.RESTABLECER_PASSWORD,
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.Container(
                    alignment=ft.Alignment.CENTER,
                    padding=24,
                    content=contenedor_ancho_limitado(
                        page, ft.AutofillGroup(content=formulario), tokens.ANCHO_FORMULARIO_AUTH
                    ),
                ),
            )
        ],
    )
