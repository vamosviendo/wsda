from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from wagtail.blocks import StreamValue


def test_home_page(browser, site, homepage, area_page, objeto_imagen):
    # Dada una portada con un container que incluye una franja
    homepage.body = StreamValue(
        homepage.body.stream_block,
        [
            (
                "franja",
                {
                    "imagen": objeto_imagen,
                    "url": {
                        "link_to": "custom_url",
                        "custom_url": area_page.url,
                    }
                }
            )
        ]
    )
    homepage.save_revision().publish()

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
