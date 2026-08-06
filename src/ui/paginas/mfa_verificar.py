import flet as ft

import estado_navegacion
import rutas
from api import sesion
from api.cliente import ApiFallo
from api.mfa import verificar_codigo
from diseno import tokens
from ui.componentes.contenedor_responsivo import contenedor_ancho_limitado


def vista_mfa_verificar(page: ft.Page) -> ft.View:
    token = estado_navegacion.obtener_token_mfa_pendiente()

    campo_codigo = ft.TextField(
        label="Código de verificación",
        hint_text="123456",
        max_length=6,
        keyboard_type=ft.KeyboardType.NUMBER,
        text_align=ft.TextAlign.CENTER,
        autofocus=True,
    )
    texto_error = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    boton_verificar = ft.Button(content="Verificar")

    def mostrar_error(mensaje: str) -> None:
        texto_error.value = mensaje
        texto_error.visible = True
        page.update()

    async def al_verificar(e: ft.Event[ft.Button]) -> None:
        codigo = campo_codigo.value.strip()
        if not token:
            page.navigate(rutas.LOGIN)
            return
        if len(codigo) != 6 or not codigo.isdigit():
            mostrar_error("El código debe ser de 6 dígitos.")
            return

        texto_error.visible = False
        boton_verificar.disabled = True
        boton_verificar.content = "Verificando..."
        page.update()

        resultado = await verificar_codigo(token, codigo)

        boton_verificar.disabled = False
        boton_verificar.content = "Verificar"

        if isinstance(resultado, ApiFallo):
            mostrar_error(resultado.error.mensaje)
            return

        estado_navegacion.limpiar()
        caso = resultado.datos
        await sesion.guardar_tokens(caso.access_token, caso.refresh_token)
        await sesion.guardar_empresa_activa(caso.empresa_id)
        page.navigate(rutas.DASHBOARD)

    boton_verificar.on_click = al_verificar
    campo_codigo.on_submit = al_verificar

    if not token:
        page.navigate(rutas.LOGIN)

    formulario = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        controls=[
            ft.Text(
                "Verificación en dos pasos",
                theme_style=ft.TextThemeStyle.HEADLINE_LARGE,
            ),
            ft.Text(
                "Ingresá el código de 6 dígitos de tu aplicación autenticadora.",
                theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                color=tokens.GRAFITO,
            ),
            campo_codigo,
            texto_error,
            boton_verificar,
        ],
    )

    return ft.View(
        route=rutas.MFA_VERIFICAR,
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
