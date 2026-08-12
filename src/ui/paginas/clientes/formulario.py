import re
from typing import Awaitable, Callable, Optional

import flet as ft

import catalogos
import rutas
import validacion
from api.cliente import ApiFallo, ApiResultado
from api.cliente_autenticado import SesionExpirada
from api.clientes import ActividadHacienda, Cliente, DatosCliente, consultar_hacienda
from diseno import tokens
from ui.componentes.bloque_ubicacion import construir_bloque_ubicacion


def construir_formulario_cliente(
    page: ft.Page,
    cliente_inicial: Optional[Cliente],
    guardar: Callable[[DatosCliente], Awaitable[ApiResultado]],
    al_exito: Callable[[object], None],
    texto_boton: str = "Guardar",
) -> ft.Column:
    c = cliente_inicial

    campo_nombre = ft.TextField(label="Nombre", max_length=255, value=c.nombre if c else "")
    campo_tipo_identificacion = ft.Dropdown(
        label="Tipo de identificación",
        value=c.tipo_identificacion if c else None,
        options=[
            ft.DropdownOption(key=clave, text=f"{clave} — {etiqueta}")
            for clave, etiqueta in catalogos.TIPOS_IDENTIFICACION
        ],
    )
    campo_numero_identificacion = ft.TextField(
        label="Número de identificación",
        max_length=20,
        value=c.numero_identificacion if c else "",
        expand=True,
    )
    boton_buscar_hacienda = ft.Button(content="Buscar en Hacienda")
    texto_estado_hacienda = ft.Text(value="", theme_style=ft.TextThemeStyle.BODY_SMALL, visible=False)

    # campo_codigo_actividad sigue siendo la fuente de verdad que lee al_guardar (sin cambios
    # ahí) -- cuando Hacienda devuelve actividades activas, se oculta y un Dropdown paralelo
    # toma su lugar visualmente, reflejando la selección en campo_codigo_actividad.value.
    campo_codigo_actividad = ft.TextField(
        label="Código de actividad",
        max_length=6,
        value=(c.codigo_actividad or "") if c else "",
    )
    campo_codigo_actividad_dropdown = ft.Dropdown(
        label="Código de actividad",
        options=[],
        visible=False,
        hint_text="Actividades económicas activas reportadas por Hacienda",
    )
    estado_hacienda: dict = {"actividades": [], "ultima_busqueda_automatica": None}

    columnas_ubicacion = {"xs": 12, "sm": 6}
    bloque_ubicacion = construir_bloque_ubicacion(page, col=columnas_ubicacion)
    campo_provincia = bloque_ubicacion.provincia
    campo_canton = bloque_ubicacion.canton
    campo_distrito = bloque_ubicacion.distrito
    if c:
        campo_provincia.value = c.codigo_provincia or None
        campo_canton.value = c.canton or None
        campo_distrito.value = c.distrito or None
    campo_otras_senas = ft.TextField(
        label="Otras señas",
        max_length=300,
        multiline=True,
        max_lines=2,
        value=(c.otras_senas or "") if c else "",
        col=columnas_ubicacion,
    )

    campo_telefono = ft.TextField(
        label="Teléfono", max_length=20, value=(c.telefono or "") if c else ""
    )
    campo_email = ft.TextField(
        label="Correo electrónico",
        max_length=255,
        keyboard_type=ft.KeyboardType.EMAIL,
        value=(c.email or "") if c else "",
    )
    campo_requiere_fe = ft.Switch(
        label="Requiere factura electrónica",
        value=c.requiere_factura_electronica if c is not None else True,
    )

    texto_error = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    boton_guardar = ft.Button(content=texto_boton)

    def limpiar_errores() -> None:
        for campo in (
            campo_nombre,
            campo_numero_identificacion,
            campo_otras_senas,
            campo_email,
        ):
            campo.error = None
        for campo in (campo_provincia, campo_canton, campo_distrito):
            campo.error_text = None
        campo_tipo_identificacion.error_text = None
        texto_error.visible = False

    def mostrar_error_general(mensaje: str) -> None:
        texto_error.value = mensaje
        texto_error.visible = True
        page.update()

    def mostrar_estado_hacienda(mensaje: str, *, exito: bool) -> None:
        texto_estado_hacienda.value = mensaje
        texto_estado_hacienda.color = tokens.ESTADO_ACEPTADO if exito else tokens.ESTADO_RECHAZADO
        texto_estado_hacienda.visible = True
        page.update()

    def actualizar_actividades(activas: list[ActividadHacienda]) -> None:
        estado_hacienda["actividades"] = activas
        if not activas:
            campo_codigo_actividad_dropdown.visible = False
            campo_codigo_actividad.visible = True
            return

        principal = next((a for a in activas if a.tipo == "P"), activas[0])
        campo_codigo_actividad_dropdown.options = [
            ft.DropdownOption(
                key=a.codigo,
                text=f"{a.codigo} — {a.descripcion}" + (" (Principal)" if a.tipo == "P" else ""),
            )
            for a in activas
        ]
        campo_codigo_actividad_dropdown.value = principal.codigo
        campo_codigo_actividad.value = principal.codigo
        campo_codigo_actividad_dropdown.visible = True
        campo_codigo_actividad.visible = False

    def al_cambiar_actividad(e: ft.Event[ft.Dropdown]) -> None:
        campo_codigo_actividad.value = e.control.value
        page.update()

    campo_codigo_actividad_dropdown.on_select = al_cambiar_actividad

    async def al_buscar_hacienda(e: Optional[ft.Event] = None) -> None:
        identificacion = (campo_numero_identificacion.value or "").strip()
        if not identificacion:
            campo_numero_identificacion.error = "Ingresá un número de identificación para buscar"
            page.update()
            return
        campo_numero_identificacion.error = None

        boton_buscar_hacienda.disabled = True
        boton_buscar_hacienda.content = "Buscando..."
        page.update()

        try:
            resultado = await consultar_hacienda(identificacion)
        except SesionExpirada:
            page.navigate(rutas.LOGIN)
            return

        boton_buscar_hacienda.disabled = False
        boton_buscar_hacienda.content = "Buscar en Hacienda"

        if isinstance(resultado, ApiFallo):
            mostrar_estado_hacienda("Error al consultar Hacienda. Intentá de nuevo.", exito=False)
            return

        datos = resultado.datos
        if datos.exitosa and datos.nombre:
            campo_nombre.value = datos.nombre
            if datos.tipo_identificacion:
                campo_tipo_identificacion.value = datos.tipo_identificacion
            actualizar_actividades([a for a in datos.actividades if a.estado == "A"])
            mostrar_estado_hacienda("Datos completados desde Hacienda", exito=True)
        else:
            actualizar_actividades([])
            mostrar_estado_hacienda(
                datos.mensaje_error or "No se encontró esa identificación en Hacienda", exito=False
            )

    boton_buscar_hacienda.on_click = al_buscar_hacienda

    # Dispara la búsqueda sola apenas numeroIdentificacion llega a la cantidad de caracteres
    # que Hacienda espera para el tipoIdentificacion seleccionado (catalogos.LONGITUDES_
    # IDENTIFICACION) -- evita que el usuario tenga que acordarse de tocar el botón. El dict
    # de estado evita reintentar la misma consulta en cada evento, pero sigue permitiendo
    # re-disparar si el valor cambia (p. ej. DIMEX pasando de 11 a 12 caracteres tras un
    # primer miss).
    async def verificar_auto_busqueda() -> None:
        if boton_buscar_hacienda.disabled:
            return
        tipo = campo_tipo_identificacion.value
        longitudes = catalogos.LONGITUDES_IDENTIFICACION.get(tipo) if tipo else None
        if not longitudes:
            return

        numero_limpio = re.sub(r"[\s-]", "", campo_numero_identificacion.value or "")
        if len(numero_limpio) not in longitudes:
            return
        if estado_hacienda["ultima_busqueda_automatica"] == numero_limpio:
            return

        estado_hacienda["ultima_busqueda_automatica"] = numero_limpio
        await al_buscar_hacienda()

    async def al_cambiar_numero_identificacion(e: ft.Event[ft.TextField]) -> None:
        await verificar_auto_busqueda()

    async def al_cambiar_tipo_identificacion(e: ft.Event[ft.Dropdown]) -> None:
        await verificar_auto_busqueda()

    campo_numero_identificacion.on_change = al_cambiar_numero_identificacion
    campo_tipo_identificacion.on_select = al_cambiar_tipo_identificacion

    def validar() -> bool:
        valido = True

        if not campo_nombre.value.strip():
            campo_nombre.error = "Requerido"
            valido = False
        if not campo_tipo_identificacion.value:
            campo_tipo_identificacion.error_text = "Seleccioná un tipo"
            valido = False
        if not campo_numero_identificacion.value.strip():
            campo_numero_identificacion.error = "Requerido"
            valido = False
        if campo_email.value.strip() and not validacion.email_valido(campo_email.value.strip()):
            campo_email.error = "Email inválido"
            valido = False

        errores_ubicacion = validacion.bloque_todo_o_nada(
            {
                "provincia": campo_provincia.value or "",
                "canton": campo_canton.value or "",
                "distrito": campo_distrito.value or "",
                "otras_senas": campo_otras_senas.value,
            }
        )
        mapa_dropdowns_ubicacion = {
            "provincia": campo_provincia,
            "canton": campo_canton,
            "distrito": campo_distrito,
        }
        for clave, mensaje in errores_ubicacion.items():
            if clave == "otras_senas":
                campo_otras_senas.error = mensaje
            else:
                mapa_dropdowns_ubicacion[clave].error_text = mensaje
            valido = False

        if not errores_ubicacion and all(
            (v.value or "").strip()
            for v in (campo_provincia, campo_canton, campo_distrito, campo_otras_senas)
        ):
            if len(campo_otras_senas.value.strip()) < 5:
                campo_otras_senas.error = "Mínimo 5 caracteres"
                valido = False

        return valido

    async def al_guardar(e: ft.Event[ft.Button]) -> None:
        limpiar_errores()
        page.update()

        if not validar():
            page.update()
            return

        boton_guardar.disabled = True
        boton_guardar.content = "Guardando..."
        page.update()

        datos = DatosCliente(
            nombre=campo_nombre.value,
            tipo_identificacion=campo_tipo_identificacion.value,
            numero_identificacion=campo_numero_identificacion.value,
            codigo_actividad=campo_codigo_actividad.value,
            codigo_provincia=campo_provincia.value or "",
            canton=campo_canton.value or "",
            distrito=campo_distrito.value or "",
            otras_senas=campo_otras_senas.value,
            telefono=campo_telefono.value,
            email=campo_email.value,
            requiere_factura_electronica=campo_requiere_fe.value,
        )

        try:
            resultado = await guardar(datos)
        except SesionExpirada:
            page.navigate(rutas.LOGIN)
            return

        boton_guardar.disabled = False
        boton_guardar.content = texto_boton

        if isinstance(resultado, ApiFallo):
            mostrar_error_general(resultado.error.mensaje)
            return

        al_exito(resultado.datos)

    boton_guardar.on_click = al_guardar
    # campo_otras_senas queda afuera: es multilinea, Enter ahí inserta un
    # salto de línea en vez de enviar el formulario. provincia/canton/distrito
    # quedan afuera también: son Dropdown, no tienen on_submit.
    for campo in (
        campo_nombre,
        campo_numero_identificacion,
        campo_codigo_actividad,
        campo_telefono,
        campo_email,
    ):
        campo.on_submit = al_guardar

    page.run_task(bloque_ubicacion.cargar_provincias)
    page.run_task(bloque_ubicacion.sincronizar_cascada)

    return ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        controls=[
            campo_nombre,
            campo_tipo_identificacion,
            ft.Row(controls=[campo_numero_identificacion, boton_buscar_hacienda]),
            ft.Text(
                "Completa nombre y tipo de identificación automáticamente si Hacienda "
                "encuentra el contribuyente.",
                theme_style=ft.TextThemeStyle.BODY_SMALL,
                color=tokens.GRAFITO,
            ),
            texto_estado_hacienda,
            campo_codigo_actividad,
            campo_codigo_actividad_dropdown,
            ft.Text(
                "Bloque de ubicación: completá los cuatro campos juntos, o "
                "ninguno.",
                theme_style=ft.TextThemeStyle.BODY_SMALL,
                color=tokens.GRAFITO,
            ),
            ft.ResponsiveRow(
                controls=[
                    campo_provincia,
                    campo_canton,
                    campo_distrito,
                    campo_otras_senas,
                ]
            ),
            campo_telefono,
            campo_email,
            campo_requiere_fe,
            texto_error,
            boton_guardar,
        ],
    )
