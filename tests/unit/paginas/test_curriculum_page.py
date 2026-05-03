import pytest
from django.core.exceptions import ValidationError
from pytest_django import asserts
from wagtail.blocks import StreamValue

from paginas.models import CurriculumPage


@pytest.fixture
def curriculum_page(test_page):
    return test_page(
        page_type=CurriculumPage,
        title="Curriculum",
        slug="curriculum",
    )


def test_devuelve_200(curriculum_page, client):
    response = client.get(curriculum_page.url)
    assert response.status_code == 200


def test_usa_template_correcto(curriculum_page, client):
    response = client.get(curriculum_page.url)
    asserts.assertTemplateUsed(response, "paginas/curriculum_page.html")


def test_muestra_entradas_ordenadas_inversamente_por_anio(curriculum_page, client):
    stream_value = StreamValue(
        curriculum_page.entradas.stream_block,
        [
            ("entrada", {"anio": "2020", "titulo": "Primera", "lugar": "", "nota": ""}),
            ("entrada", {"anio": "2023", "titulo": "Tercera", "lugar": "", "nota": ""}),
            ("entrada", {"anio": "2021", "titulo": "Segunda", "lugar": "", "nota": ""}),
        ],
        is_lazy=False,
    )
    curriculum_page.entradas = stream_value
    curriculum_page.save()

    response = client.get(curriculum_page.url)
    fechas_entrada = [e.value['anio'] for e in response.context["entradas_ordenadas"]]
    assert fechas_entrada == ["2023", "2021", "2020"]


@pytest.mark.parametrize("anio_valido", ["1900", "1999", "2000", "2023", "2099"])
def test_entrada_acepta_anio_valido(anio_valido, curriculum_page):
    stream_block = curriculum_page.entradas.stream_block
    stream_value = StreamValue(
        stream_block,
        [(
            "entrada",
            {"anio": anio_valido, "titulo": "Test", "lugar": "", "nota": ""}
        )],
        is_lazy=False,
    )
    try:
        stream_block.clean(stream_value)
    except ValidationError:
        raise AssertionError(f"No acepta año válido: {anio_valido}")


@pytest.mark.parametrize("anio_invalido", ["23", "20234", "1a2b", "1899", "2100"])
def test_entrada_no_acepta_anio_invalido(anio_invalido, curriculum_page):
    stream_block = curriculum_page.entradas.stream_block
    stream_value = StreamValue(
        stream_block,
        [(
            "entrada",
            {"anio": anio_invalido, "titulo": "Test", "lugar": "", "nota": ""}
        )],
        is_lazy=False,
    )
    with pytest.raises(ValidationError):
        stream_block.clean(stream_value)
