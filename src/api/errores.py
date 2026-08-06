from dataclasses import dataclass
from typing import Any


@dataclass
class ErrorApi:
    mensaje: str
    status: int


def normalizar_error(status: int, cuerpo: Any) -> ErrorApi:
    """El backend devuelve MensajeResponse{mensaje} de forma uniforme para errores."""
    if isinstance(cuerpo, dict) and isinstance(cuerpo.get("mensaje"), str):
        return ErrorApi(mensaje=cuerpo["mensaje"], status=status)
    return ErrorApi(mensaje="Ocurrió un error inesperado.", status=status)
