import flet as ft

import estado_navegacion
import rutas
from api import sesion
from api.auth import AccessToken, MfaPendiente, SeleccionTenantRequerida, login
from api.cliente import ApiFallo
from diseno import tokens
from ui.componentes.contenedor_responsivo import contenedor_ancho_limitado


def vista_login(page: ft.Page) -> ft.View:
    campo_email = ft.TextField(
        label="Correo electrónico",
        hint_text="tu@correo.com",
        keyboard_type=ft.KeyboardType.EMAIL,
        autofocus=True,
        autofill_hints=[ft.AutofillHint.EMAIL],
    )
    campo_password = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        autofill_hints=[ft.AutofillHint.PASSWORD],
    )
    texto_error = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    boton_ingresar = ft.Button(content="Ingresar")

    def mostrar_error(mensaje: str) -> None:
        texto_error.value = mensaje
        texto_error.visible = True
        page.update()

    async def al_enviar(e: ft.Event[ft.Button]) -> None:
        email = campo_email.value.strip()
        password = campo_password.value

        if not email or not password:
            mostrar_error("Completá correo y contraseña.")
            return

        texto_error.visible = False
        boton_ingresar.disabled = True
        boton_ingresar.content = "Ingresando..."
        page.update()

        resultado = await login(email, password)

        boton_ingresar.disabled = False
        boton_ingresar.content = "Ingresar"

        if isinstance(resultado, ApiFallo):
            mostrar_error(resultado.error.mensaje)
            return

        caso = resultado.datos

        if isinstance(caso, AccessToken):
            try:
                await sesion.guardar_tokens(caso.access_token, caso.refresh_token)
                await sesion.guardar_empresa_activa(caso.empresa_id)
            except Exception:
                # Sin este try/except, un fallo acá (p. ej. SecureStorage sin
                # keyring/Secret Service disponible en el sistema) dejaba al
                # usuario pegado en /login sin ningún mensaje: la excepción
                # cortaba la corrutina antes de llegar al page.navigate y no
                # había ningún feedback visible de que algo había fallado.
                mostrar_error(
                    "No se pudo guardar la sesión en este dispositivo. "
                    "Verificá que haya un almacén de credenciales disponible "
                    "(keyring del sistema) e intentá de nuevo."
                )
                return
            page.navigate(rutas.DASHBOARD)
            return

        if isinstance(caso, SeleccionTenantRequerida):
            estado_navegacion.establecer_seleccion_tenant(caso.token_seleccion_tenant)
            page.navigate(rutas.SELECCIONAR_TENANT)
            return

        if isinstance(caso, MfaPendiente):
            estado_navegacion.establecer_mfa_pendiente(
                caso.token_mfa_pendiente, caso.requiere_enrolamiento
            )
            page.navigate(
                rutas.MFA_ENROLAR if caso.requiere_enrolamiento else rutas.MFA_VERIFICAR
            )
            return

    boton_ingresar.on_click = al_enviar
    campo_email.on_submit = al_enviar
    campo_password.on_submit = al_enviar

    formulario = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        controls=[
            ft.Text("Iniciar sesión", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
            ft.Text(
                "Ingresá tus credenciales para continuar.",
                theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                color=tokens.GRAFITO,
            ),
            campo_email,
            campo_password,
            texto_error,
            boton_ingresar,
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.TextButton(
                        content="¿Olvidaste tu contraseña?",
                        on_click=lambda e: page.navigate(rutas.RECUPERAR_PASSWORD),
                    ),
                ],
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        "¿No tenés cuenta?",
                        theme_style=ft.TextThemeStyle.BODY_SMALL,
                    ),
                    ft.TextButton(
                        content="Registrate",
                        on_click=lambda e: page.navigate(rutas.REGISTRO),
                    ),
                ],
            ),
        ],
    )

    return ft.View(
        route=rutas.LOGIN,
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
