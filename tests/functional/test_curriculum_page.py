import pytest
from selenium.webdriver.common.by import By
from wagtail.blocks import StreamValue

from paginas.models import CurriculumPage


@pytest.fixture
def stream_data():
    return [
        (
            "entrada",
            {
                "anio": "2022",
                "titulo": "Salón municipal de pintura Gualchi",
                "lugar": "Exaltación de la Cruz, Provincia de Buenos Aires",
                "nota": "<p>Primer premio</p>",
            },
        )
    ]


def test_curriculum_page_visitante(browser, test_page, stream_data):
    curriculum_page = test_page(
        page_type=CurriculumPage,
        title ="Curriculum",
        slug="curriculum",
        show_in_menus=True,
    )
    curriculum_page.entradas = StreamValue(
        curriculum_page.entradas.stream_block,
        stream_data,
        is_lazy=False,
    )
    curriculum_page.save_revision().publish()

    # El visitante ve la opción "curriculum" en el menú de navegación.
    browser.get_page()
    nav = browser.wait_for("nav")
    enlaces = nav.find_elements(By.TAG_NAME, "a")
    enlace_curriculum = next(
        (a for a in enlaces if "curriculum" in a.text.lower()),
        None
    )
    assert \
        enlace_curriculum is not None, \
        "El visitante no encontró 'Curriculum' en el menú de navegación"

    # El visitante cliquea en la opción currículum y va a la página de curriculum
    enlace_curriculum.click()
    assert curriculum_page.url in browser.current_url

    # Dentro de la página, ve el encabezado "Muestras, premios y salones"
    heading = browser.wait_for("h2.page-titulo")
    assert "Muestras, premios y salones" in heading.text

    # A continuación del encabezado, ve las entradas del curriculum
    browser.get_page(curriculum_page.url)
    body_text = browser.wait_for("body").text
    assert "2022" in body_text
    assert "Salón municipal de pintura Gualchi" in body_text
    assert "Exaltación de la Cruz" in body_text
    assert "Primer premio" in body_text
