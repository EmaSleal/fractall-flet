import flet.testing as ftt

import main


async def test_arranca_sin_errores(flet_app: ftt.FletTestApp):
    tester = flet_app.tester
    await tester.pump_and_settle()

    assert (await tester.find_by_text_containing("Andamiaje listo")).count == 1


def test_main_expone_funcion_main():
    assert callable(main.main)
