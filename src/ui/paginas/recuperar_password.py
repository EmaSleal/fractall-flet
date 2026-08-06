import flet as ft

import rutas
import validacion
from api.auth import recuperar_password
from api.cliente import ApiFallo
from diseno import tokens
from ui.componentes.contenedor_responsivo import contenedor_ancho_limitado


def vista_recuperar_password(page: ft.Page) -> ft.View:
    campo_email = ft.TextField(
        label="Correo electrónico",
        hint_text="tu@correo.com",
        keyboard_type=ft.KeyboardType.EMAIL,
        autofocus=True,
        autofill_hints=[ft.AutofillHint.EMAIL],
    )
    texto_error = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    boton_enviar = ft.Button(content="Enviar instrucciones")

    def mostrar_error(mensaje: str) -> None:
        texto_error.value = mensaje
        texto_error.visible = True
        page.update()

    def vista_exito() -> ft.View:
        contenido_exito = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            controls=[
                ft.Text("Revisá tu correo", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
                ft.Text(
                    "Si el correo está registrado, te enviamos instrucciones "
                    "para restablecer tu contraseña.",
                    theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                    color=tokens.GRAFITO,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Button(
                    content="Ya tengo un código",
                    on_click=lambda e: page.navigate(rutas.RESTABLECER_PASSWORD),
                ),
                ft.TextButton(
                    content="Volver a iniciar sesión",
                    on_click=lambda e: page.navigate(rutas.LOGIN),
                ),
            ],
        )
        return ft.View(
            route=rutas.RECUPERAR_PASSWORD,
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
        email = campo_email.value.strip()
        if not validacion.email_valido(email):
            mostrar_error("Ingresá un correo electrónico válido.")
            return

        texto_error.visible = False
        boton_enviar.disabled = True
        boton_enviar.content = "Enviando..."
        page.update()

        resultado = await recuperar_password(email)

        boton_enviar.disabled = False
        boton_enviar.content = "Enviar instrucciones"

        if isinstance(resultado, ApiFallo):
            mostrar_error(resultado.error.mensaje)
            return

        page.views[-1] = vista_exito()
        page.update()

    boton_enviar.on_click = al_enviar
    campo_email.on_submit = al_enviar

    formulario = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        controls=[
            ft.Text("Recuperar contraseña", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
            ft.Text(
                "Ingresá tu correo y te enviamos instrucciones para "
                "restablecer tu contraseña.",
                theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                color=tokens.GRAFITO,
            ),
            campo_email,
            texto_error,
            boton_enviar,
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
        route=rutas.RECUPERAR_PASSWORD,
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
