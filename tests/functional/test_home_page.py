import os

import pytest

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from wagtail.blocks import StreamValue


@pytest.fixture
def homepage_con_franja(remote_fixtures, homepage, area_page, objeto_imagen):
    if os.environ.get("TEST_SERVER"):
        remote_fixtures.set_homepage_franja(
            area_url = area_page.url,
            imagen_path = objeto_imagen.path,
        )
        return area_page

    homepage.body = StreamValue(
        homepage.body.stream_block,
        [("franja", {
            "imagen": objeto_imagen,
            "url": {"link_to": "custom_url", "custom_url": area_page.url},
        })],
        is_lazy=False,
    )
    homepage.save_revision().publish()
    return area_page



def test_home_page(browser, homepage_con_franja):
    # Dada una portada con un container que incluye una franja
    area_page = homepage_con_franja

    # La portada carga sin errores
    browser.get_page()
    title = browser.title
    assert "error" not in title.lower()
    assert "not found" not in title.lower()

    # La portada muestra el container franjas
    try:
        browser.wait_for("#franjas")
    except TimeoutException:
        raise AssertionError("No se encontró el elemento .franjas")

    # Si el container contiene franjas, al cliquear en ellas se llega a la
    # sección correspondiente.
    browser.find_elements(By.CSS_SELECTOR, ".franja")[0].click()
    assert area_page.url in browser.current_url


def test_aplica_css(browser, site):
    browser.get_page()
    site_title = browser.wait_for("#site-title")
    font_family = browser.get_computed_style(site_title, "fontFamily")
    # Nos aseguramos de que no es el font genérico del sistema (serif/Times)
    # indicando que el CSS efectivamente cargó.
    assert font_family != "Times New Roman"
    assert font_family != "serif"
