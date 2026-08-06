from datetime import datetime
from typing import Optional


def formatear_fecha(iso: Optional[str]) -> str:
    if not iso:
        return "Sin vencimiento"
    try:
        valor = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return iso
    return valor.strftime("%d/%m/%Y")


def fecha_a_iso(valor: datetime) -> str:
    return valor.strftime("%Y-%m-%d")


_SIMBOLOS_MONEDA = {"CRC": "₡", "USD": "$"}


def formatear_moneda(valor: float, moneda: str = "CRC") -> str:
    simbolo = _SIMBOLOS_MONEDA.get(moneda, moneda + " ")
    return f"{simbolo}{valor:,.2f}"
