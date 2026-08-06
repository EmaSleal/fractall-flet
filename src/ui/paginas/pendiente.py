import flet as ft


def vista_pendiente(ruta: str) -> ft.View:
    return ft.View(
        route=ruta,
        controls=[
            ft.SafeArea(
                expand=True,
                content=ft.Container(
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text("Pantalla en construcción", size=18),
                            ft.Text(ruta, size=12),
                        ],
                    ),
                ),
            )
        ],
    )
