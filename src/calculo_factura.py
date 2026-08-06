"""Cálculos puros del wizard de facturas, portados de
fractall-frontend/app/(app)/facturas/nueva/reducer.ts. El IVA acá es solo
una estimación visual — el backend es la autoridad final y nunca recibe
`totalImpuesto`/`total` en el request. El único chequeo bloqueante real es
que los medios de pago sumen el total exacto, comparado en centavos
enteros (ver a_centavos)."""

import math


def a_centavos(monto: float) -> int:
    """Replica Math.round de JS (redondeo hacia arriba en el .5) en vez del
    banker's rounding de round() de Python — evita drift de punto flotante
    al comparar sumas de dinero. Válido para montos no negativos (precios,
    totales), que es el único caso de uso acá."""
    return math.floor(monto * 100 + 0.5)


def calcular_subtotal_linea(cantidad: float, precio_unitario: float, descuento_monto: float) -> float:
    return cantidad * precio_unitario - descuento_monto


def calcular_iva_linea(
    cantidad: float, precio_unitario: float, descuento_monto: float, porcentaje_impuesto: float
) -> float:
    return calcular_subtotal_linea(cantidad, precio_unitario, descuento_monto) * (
        porcentaje_impuesto / 100
    )


def calcular_subtotal_factura(lineas) -> float:
    return sum(
        calcular_subtotal_linea(linea.cantidad, linea.precio_unitario, linea.descuento_monto)
        for linea in lineas
    )


def calcular_iva_total(lineas) -> float:
    return sum(
        calcular_iva_linea(
            linea.cantidad, linea.precio_unitario, linea.descuento_monto, linea.porcentaje_impuesto
        )
        for linea in lineas
    )


def calcular_total_factura(lineas, otros_cargos=()) -> float:
    return (
        calcular_subtotal_factura(lineas)
        + calcular_iva_total(lineas)
        + sum(cargo.monto_cargo for cargo in otros_cargos)
    )


def calcular_total_medios_pago(medios_pago) -> float:
    return sum(medio.total_medio_pago for medio in medios_pago)


def coincide_total_medios_pago(medios_pago, total_factura: float) -> bool:
    suma_centavos = sum(a_centavos(medio.total_medio_pago) for medio in medios_pago)
    return suma_centavos == a_centavos(total_factura)


def calcular_delta_medios_pago(medios_pago, total_factura: float) -> float:
    return calcular_total_medios_pago(medios_pago) - total_factura
