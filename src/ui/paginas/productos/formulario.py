from typing import Awaitable, Callable, Optional

import flet as ft

import formato
import rutas
from api.cabys import CabysResultado
from api.cliente import ApiFallo, ApiResultado
from api.cliente_autenticado import SesionExpirada
from api.productos import DatosProducto, Producto
from api.unidades_medida import UnidadMedida
from diseno import tokens
from ui.componentes.buscador_cabys import construir_buscador_cabys
from ui.componentes.selector_unidad_medida import construir_selector_unidad_medida


def construir_formulario_producto(
    page: ft.Page,
    producto_inicial: Optional[Producto],
    unidades_medida: list[UnidadMedida],
    guardar: Callable[[DatosProducto], Awaitable[ApiResultado]],
    al_exito: Callable[[object], None],
    texto_boton: str = "Guardar",
) -> ft.Column:
    p = producto_inicial

    campo_codigo = ft.TextField(label="Código", max_length=50, value=p.codigo if p else "")
    campo_descripcion = ft.TextField(
        label="Descripción", max_length=255, value=p.descripcion if p else ""
    )

    estado_cabys = {"codigo": p.codigo_cabys if p else None}

    def al_elegir_cabys(item: CabysResultado) -> None:
        estado_cabys["codigo"] = item.codigo

    valor_inicial_cabys = ""
    if p and p.codigo_cabys:
        valor_inicial_cabys = f"{p.codigo_cabys} — {p.descripcion_cabys or ''}"
    buscador_cabys = construir_buscador_cabys(page, al_elegir_cabys, valor_inicial_cabys)

    controles_cabys = [buscador_cabys]
    if p and p.cabys_validado_en:
        controles_cabys.append(
            ft.Text(
                f"Validado el {formato.formatear_fecha(p.cabys_validado_en)}",
                theme_style=ft.TextThemeStyle.BODY_SMALL,
                color=tokens.GRAFITO,
            )
        )

    estado_unidad = {"codigo": p.codigo_unidad_fe if p else None}

    def al_elegir_unidad(item: UnidadMedida) -> None:
        estado_unidad["codigo"] = item.codigo

    if unidades_medida:
        valor_inicial_unidad = ""
        if p and p.codigo_unidad_fe:
            unidad_actual = next(
                (u for u in unidades_medida if u.codigo == p.codigo_unidad_fe), None
            )
            valor_inicial_unidad = (
                f"{unidad_actual.codigo} — {unidad_actual.descripcion}"
                if unidad_actual
                else p.codigo_unidad_fe
            )
        campo_unidad = construir_selector_unidad_medida(
            unidades_medida, al_elegir_unidad, valor_inicial_unidad
        )
    else:
        campo_unidad = ft.TextField(
            label="Unidad de medida (Hacienda)",
            hint_text="Ej: Sp, Unid",
            max_length=20,
            value=(p.codigo_unidad_fe or "") if p else "",
        )

    campo_precio = ft.TextField(
        label="Precio de venta",
        keyboard_type=ft.KeyboardType.NUMBER,
        value=str(p.precio_venta) if p else "",
    )
    campo_activo = ft.Switch(
        label="Activo — los productos inactivos no aparecen en las facturas",
        value=p.activo if p is not None else True,
    )

    texto_error = ft.Text(value="", color=tokens.ESTADO_RECHAZADO, visible=False)
    boton_guardar = ft.Button(content=texto_boton)

    def limpiar_errores() -> None:
        for campo in (campo_codigo, campo_descripcion, campo_precio):
            campo.error = None
        texto_error.visible = False

    def mostrar_error_general(mensaje: str) -> None:
        texto_error.value = mensaje
        texto_error.visible = True
        page.update()

    async def al_guardar(e: ft.Event[ft.Button]) -> None:
        limpiar_errores()
        page.update()

        valido = True
        if not campo_codigo.value.strip():
            campo_codigo.error = "Requerido"
            valido = False
        if not campo_descripcion.value.strip():
            campo_descripcion.error = "Requerido"
            valido = False
        if not estado_cabys["codigo"]:
            mostrar_error_general("Elegí un código CABYS de la lista de resultados.")
            valido = False

        try:
            precio = float(campo_precio.value.replace(",", "."))
            if precio < 0:
                raise ValueError
        except (ValueError, AttributeError):
            campo_precio.error = "Debe ser un número mayor o igual a 0"
            valido = False
            precio = 0.0

        if not valido:
            page.update()
            return

        boton_guardar.disabled = True
        boton_guardar.content = "Guardando..."
        page.update()

        codigo_unidad_fe = (
            campo_unidad.value
            if isinstance(campo_unidad, ft.TextField)
            else estado_unidad["codigo"]
        )
        datos = DatosProducto(
            codigo=campo_codigo.value,
            descripcion=campo_descripcion.value,
            codigo_cabys=estado_cabys["codigo"],
            codigo_unidad_fe=codigo_unidad_fe or "",
            precio_venta=precio,
            activo=campo_activo.value,
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
    campo_codigo.on_submit = al_guardar
    campo_descripcion.on_submit = al_guardar
    campo_precio.on_submit = al_guardar
    if isinstance(campo_unidad, ft.TextField):
        campo_unidad.on_submit = al_guardar

    return ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
        controls=[
            campo_codigo,
            campo_descripcion,
            *controles_cabys,
            campo_unidad,
            campo_precio,
            campo_activo,
            texto_error,
            boton_guardar,
        ],
    )
