import flet as ft

import rutas
from ui.paginas.pendiente import vista_pendiente


def vista_dashboard(page: ft.Page) -> ft.View:
    """No tiene contenido propio — igual que fractall-frontend
    (`app/(app)/dashboard/page.tsx` solo hace `redirect('/facturas')`, sin
    resumen/analítica en v1). Ahora que existe el shell con sidebar, no
    hace falta un landing intermedio con links a los mismos módulos."""
    page.navigate(rutas.FACTURAS)
    return vista_pendiente(rutas.DASHBOARD)
