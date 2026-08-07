import traceback

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

        # Todo el cuerpo va en un único try/except: Flet no imprime nada por
        # consola cuando una excepción no atajada corta una corrutina de
        # evento en el build empaquetado (confirmado con el fallo de
        # guardar_tokens), así que sin esto cualquier excepción acá deja al
        # usuario pegado en /login sin ningún rastro de qué pasó. El
        # traceback explícito es lo único que nos deja ver el error real.
        try:
            resultado = await login(email, password)

            boton_ingresar.disabled = False
            boton_ingresar.content = "Ingresar"

            if isinstance(resultado, ApiFallo):
                mostrar_error(resultado.error.mensaje)
                return

            caso = resultado.datos

            if isinstance(caso, AccessToken):
                await sesion.guardar_tokens(caso.access_token, caso.refresh_token)
                await sesion.guardar_empresa_activa(caso.empresa_id)
                # page.navigate() es "asyncio.create_task(push_route(...))" sin
                # esperar esa tarea — dentro de un handler async como este, la
                # tarea queda huérfana y puede perderse cuando la corrutina
                # termina. La doc de Flet es explícita: en contextos async hay
                # que usar `await page.push_route(...)` en su lugar.
                await page.push_route(rutas.DASHBOARD)
                return

            if isinstance(caso, SeleccionTenantRequerida):
                estado_navegacion.establecer_seleccion_tenant(caso.token_seleccion_tenant)
                await page.push_route(rutas.SELECCIONAR_TENANT)
                return

            if isinstance(caso, MfaPendiente):
                estado_navegacion.establecer_mfa_pendiente(
                    caso.token_mfa_pendiente, caso.requiere_enrolamiento
                )
                await page.push_route(
                    rutas.MFA_ENROLAR if caso.requiere_enrolamiento else rutas.MFA_VERIFICAR
                )
                return
        except Exception:
            traceback.print_exc()
            boton_ingresar.disabled = False
            boton_ingresar.content = "Ingresar"
            mostrar_error(
                "Ocurrió un error inesperado al iniciar sesión. "
                "Revisá la consola para más detalles."
            )

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
