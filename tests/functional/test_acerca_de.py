import os

import pytest
from selenium.webdriver.common.by import By

from paginas.models import AcercaDePage


@pytest.fixture
def texto():
    return (
        "Liliana Medela nació en Buenos Aires en 1956. "
        "Su obra explora la relación entre el espacio "
        "y la materia"
    )

@pytest.fixture
def acerca_page(remote_fixtures, test_page, texto):
    if os.environ.get("TEST_SERVER"):
        return remote_fixtures.crear_pagina_simple(
            tipo="acerca_de",
            title="Acerca de",
            page_data={
                "titulo": "Acerca del artista",
                "body": f"<p>{texto}</p>"
            },
            show_in_menus=True,
        )

    acerca_page_draft = test_page(
        page_type=AcercaDePage,
        title="Acerca de",
        publish=False,
        titulo="Acerca del artista",
        show_in_menus=True,
    )
    acerca_page_draft.body = f"<p>{texto}<p>"
    revision = acerca_page_draft.save_revision()
    revision.publish()
    return acerca_page_draft


def test_admin_publica_y_visitante_lee(
        browser, acerca_page, texto):
    # El visitante abre el sitio, encuentra "Acerca de" en el menú de
    # navegación, hace clic y lee la biografía completa.
    browser.get_page()
    nav = browser.wait_for("nav")
    enlaces = nav.find_elements(By.TAG_NAME, "a")
    enlace = next(x for x in enlaces if "acerca" in x.text.lower())
    assert enlace is not None, "El visitante no encontró 'Acerca de' en el menú de navegación"

    enlace.click()
    body_text = browser.wait_for("body").text
    assert texto in body_text, "El visitante no puede leer la biografía completa"
