import os
from pathlib import Path

from dotenv import load_dotenv

# load_dotenv() sin argumentos busca el .env recorriendo el stack de frames
# con sys._getframe(), lo cual revienta con AssertionError dentro del
# ejecutable empaquetado (runtime serious_python de flet build) porque ahí
# el stack se queda sin frames con un archivo real en disco. Se resuelve la
# ruta a mano con __file__, que sí es confiable en ambos entornos.
_AQUI = Path(__file__).resolve().parent
load_dotenv(_AQUI / ".env")  # build empaquetado: .env embebido junto a este módulo
load_dotenv(_AQUI.parent.parent / ".env")  # dev local: .env en la raíz del repo

BACKEND_URL = os.environ.get("BACKEND_URL")
if not BACKEND_URL:
    raise RuntimeError(
        "BACKEND_URL no está configurada. Definila en .env (ver .env.example)."
    )
