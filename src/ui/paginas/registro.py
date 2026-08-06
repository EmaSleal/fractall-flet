import flet as ft

import rutas
import validacion
from api.auth import registro
from api.cliente import ApiFallo
from diseno import tokens
from ui.componentes.contenedor_responsivo import contenedor_ancho_limitado


def vista_registro(page: ft.Page) -> ft.View:
    campo_nombre = ft.TextField(
        label="Nombre completo", max_length=255, autofill_hints=[ft.AutofillHint.NAME]
    )
    campo_email = ft.TextField(
        label="Correo electrónico",
        keyboard_type=ft.KeyboardType.EMAIL,
        max_length=255,
        autofill_hints=[ft.AutofillHint.EMAIL],
    )
    campo_password = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        max_length=72,
        autofill_hints=[ft.AutofillHint.NEW_PASSWORD],
    )
    campo_confirmar = ft.TextField(
        label="Confirmar contraseña",
        password=True,
        can_reveal_password=True,
        max_length=72,
        autofill_hints=[ft.AutofillHint.NEW_PASSWORD],
    )
    campo_razon_social = ft.TextField(label="Razón social", max_length=255)
    checkbox_mfa = ft.Checkbox(
        label="Activar verificación en dos pasos (MFA) para mi cuenta"
    )

    texto_error = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    boton_crear = ft.Button(content="Crear cuenta")
    lista_reglas = ft.Column(visible=False, spacing=2)

    def refrescar_reglas() -> None:
        password = campo_password.value
        if not password:
            lista_reglas.visible = False
            lista_reglas.controls = []
            return
        lista_reglas.visible = True
        lista_reglas.controls = [
            ft.Row(
                spacing=6,
                controls=[
                    ft.Icon(
                        ft.Icons.CHECK if cumple else ft.Icons.CLOSE,
                        size=12,
                        color=tokens.ESTADO_ACEPTADO if cumple else tokens.GRAFITO,
                    ),
                    ft.Text(
                        etiqueta,
                        theme_style=ft.TextThemeStyle.BODY_SMALL,
                        color=tokens.ESTADO_ACEPTADO if cumple else tokens.GRAFITO,
                    ),
                ],
            )
            for etiqueta, cumple in validacion.evaluar_password(password)
        ]

    def al_cambiar_password(e: ft.Event[ft.TextField]) -> None:
        refrescar_reglas()
        page.update()

    campo_password.on_change = al_cambiar_password

    def mostrar_error(mensaje: str) -> None:
        texto_error.value = mensaje
        texto_error.visible = True
        page.update()

    def vista_exito() -> ft.View:
        contenido_exito = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            controls=[
                ft.Text("¡Cuenta creada!", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
                ft.Text(
                    "Revisá tu correo electrónico para confirmar tu "
                    "cuenta antes de iniciar sesión.",
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
            route=rutas.REGISTRO,
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
        nombre = campo_nombre.value.strip()
        email = campo_email.value.strip()
        password = campo_password.value
        confirmar = campo_confirmar.value
        razon_social = campo_razon_social.value.strip()

        if not nombre:
            mostrar_error("El nombre es obligatorio.")
            return
        if not validacion.email_valido(email):
            mostrar_error("Ingresá un correo electrónico válido.")
            return
        if not validacion.password_valida(password):
            mostrar_error("La contraseña no cumple los requisitos mínimos.")
            return
        if password != confirmar:
            mostrar_error("Las contraseñas no coinciden.")
            return
        if not razon_social:
            mostrar_error("La razón social es obligatoria.")
            return

        texto_error.visible = False
        boton_crear.disabled = True
        boton_crear.content = "Creando cuenta..."
        page.update()

        resultado = await registro(
            nombre=nombre,
            email=email,
            password=password,
            razon_social=razon_social,
            activar_mfa=checkbox_mfa.value,
        )

        boton_crear.disabled = False
        boton_crear.content = "Crear cuenta"

        if isinstance(resultado, ApiFallo):
            mostrar_error(resultado.error.mensaje)
            return

        page.views[-1] = vista_exito()
        page.update()

    boton_crear.on_click = al_enviar
    campo_nombre.on_submit = al_enviar
    campo_email.on_submit = al_enviar
    campo_password.on_submit = al_enviar
    campo_confirmar.on_submit = al_enviar
    campo_razon_social.on_submit = al_enviar

    formulario = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        controls=[
            ft.Text("Crear cuenta", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
            ft.Text(
                "Completá los datos para registrarte en FRACTALL.",
                theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                color=tokens.GRAFITO,
            ),
            campo_nombre,
            campo_email,
            campo_password,
            lista_reglas,
            campo_confirmar,
            campo_razon_social,
            checkbox_mfa,
            texto_error,
            boton_crear,
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text("¿Ya tenés cuenta?", theme_style=ft.TextThemeStyle.BODY_SMALL),
                    ft.TextButton(
                        content="Iniciá sesión",
                        on_click=lambda e: page.navigate(rutas.LOGIN),
                    ),
                ],
            ),
        ],
    )

    return ft.View(
        route=rutas.REGISTRO,
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
