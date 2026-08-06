import flet as ft

import estado_navegacion
import rutas
from api import sesion
from api.auth import AccessToken, MfaPendiente
from api.auth import seleccionar_tenant as api_seleccionar_tenant
from api.cliente import ApiFallo
from api.perfil import obtener_mis_empresas
from diseno import tokens
from ui.componentes.contenedor_responsivo import contenedor_ancho_limitado


def vista_seleccionar_tenant(page: ft.Page) -> ft.View:
    token = estado_navegacion.obtener_token_seleccion_tenant()

    grupo_radio = ft.RadioGroup(content=ft.Column(spacing=8))
    texto_estado = ft.Text(
        "Cargando empresas...", theme_style=ft.TextThemeStyle.BODY_SMALL
    )
    texto_error = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    boton_continuar = ft.Button(content="Continuar", disabled=True)

    def mostrar_error(mensaje: str) -> None:
        texto_error.value = mensaje
        texto_error.visible = True
        page.update()

    def al_cambiar_seleccion(e: ft.Event[ft.RadioGroup]) -> None:
        boton_continuar.disabled = not grupo_radio.value
        page.update()

    grupo_radio.on_change = al_cambiar_seleccion

    async def cargar_empresas() -> None:
        resultado = await obtener_mis_empresas(token)
        if isinstance(resultado, ApiFallo):
            texto_estado.value = ""
            mostrar_error(resultado.error.mensaje)
            return

        empresas = resultado.datos
        texto_estado.visible = False
        grupo_radio.content.controls = [
            ft.Radio(value=e.empresa_id, label=e.nombre_comercial or e.razon_social)
            for e in empresas
        ]
        page.update()

    async def al_continuar(e: ft.Event[ft.Button]) -> None:
        empresa_id = grupo_radio.value
        if not empresa_id or not token:
            return

        texto_error.visible = False
        boton_continuar.disabled = True
        boton_continuar.content = "Ingresando..."
        page.update()

        resultado = await api_seleccionar_tenant(token, empresa_id)

        boton_continuar.disabled = False
        boton_continuar.content = "Continuar"

        if isinstance(resultado, ApiFallo):
            mostrar_error(resultado.error.mensaje)
            return

        estado_navegacion.limpiar()
        caso = resultado.datos

        if isinstance(caso, AccessToken):
            await sesion.guardar_tokens(caso.access_token, caso.refresh_token)
            await sesion.guardar_empresa_activa(caso.empresa_id)
            page.navigate(rutas.DASHBOARD)
            return

        if isinstance(caso, MfaPendiente):
            estado_navegacion.establecer_mfa_pendiente(
                caso.token_mfa_pendiente, caso.requiere_enrolamiento
            )
            page.navigate(
                rutas.MFA_ENROLAR if caso.requiere_enrolamiento else rutas.MFA_VERIFICAR
            )

    boton_continuar.on_click = al_continuar

    if not token:
        page.navigate(rutas.LOGIN)
    else:
        page.run_task(cargar_empresas)

    formulario = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        controls=[
            ft.Text(
                "Seleccionar empresa", theme_style=ft.TextThemeStyle.HEADLINE_LARGE
            ),
            ft.Text(
                "Tu cuenta está asociada a varias empresas. "
                "Elegí con cuál continuar.",
                theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                color=tokens.GRAFITO,
            ),
            texto_estado,
            grupo_radio,
            texto_error,
            boton_continuar,
        ],
    )

    return ft.View(
        route=rutas.SELECCIONAR_TENANT,
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
