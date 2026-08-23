import re
from typing import Optional

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

REGLAS_PASSWORD = [
    ("Mínimo 8 caracteres", lambda p: len(p) >= 8),
    ("Una mayúscula", lambda p: bool(re.search(r"[A-Z]", p))),
    ("Un número", lambda p: bool(re.search(r"[0-9]", p))),
    ("Un carácter especial (ej: ! @ # $ % & * - _ .)", lambda p: bool(re.search(r"[^a-zA-Z0-9]", p))),
]


def evaluar_password(password: str) -> list[tuple[str, bool]]:
    return [(label, prueba(password)) for label, prueba in REGLAS_PASSWORD]


def password_valida(password: str) -> bool:
    return len(password) <= 72 and all(cumple for _, cumple in evaluar_password(password))


def email_valido(email: str) -> bool:
    return len(email) <= 255 and bool(_EMAIL_RE.match(email))


def bloque_todo_o_nada(valores: dict[str, str]) -> dict[str, str]:
    """Si algunos campos del grupo (no todos) están completos, marca error
    en los vacíos. Réplica de la regla de fractall-frontend para el bloque
    de ubicación de clientes (codigoProvincia/canton/distrito/otrasSenas):
    documentada en el backend pero sin required en el schema OpenAPI, así
    que se aplica del lado del cliente para dar feedback antes de enviar.
    No aplica reglas adicionales (ej. longitud mínima) — eso queda a cargo
    del caller."""
    presentes = {k: v for k, v in valores.items() if v.strip()}
    if 0 < len(presentes) < len(valores):
        return {
            k: "Requerido si el bloque de ubicación está parcialmente completo"
            for k, v in valores.items()
            if not v.strip()
        }
    return {}


def exoneracion_requiere_institucion_otros(
    tipo_documento: str, nombre_institucion_otros: str
) -> Optional[str]:
    """Réplica del superRefine de fractall-frontend: si el tipo de
    exoneración es "99 — Otros", nombreInstitucionOtros pasa a ser
    obligatorio (el backend solo exige fechaEmision y
    porcentajeExoneracion, ver CrearClienteExoneracionRequest)."""
    if tipo_documento == "99" and not nombre_institucion_otros.strip():
        return 'Requerido cuando el tipo es "99 — Otros"'
    return None
