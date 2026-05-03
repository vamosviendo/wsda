import pytest
from django.urls import reverse
from wagtail.test.utils.form_data import rich_text, nested_form_data
from wagtail.test.utils.page_tests import WagtailPageTestCase

from home.models import HomePage
from paginas.models import AcercaDePage
from tests.conftest import authenticated_client
from utils.pytest import wagtailasserts

pagetestcase = WagtailPageTestCase()


@pytest.fixture
def texto():
    return (
        "Rogelio Roldán nació en Buenos Aires en 1956. "
        "Su obra explora la relación entre el espacio "
        "y la materia"
    )


@pytest.fixture
def acerca_de_page(test_page, texto):
    return test_page(
        page_type=AcercaDePage,
        title="Acerca de",
        titulo="Acerca de la artista",
        body=texto,
    )


@pytest.fixture
def url_creacion(homepage):
    return reverse(
        "wagtailadmin_pages:add",
        args=["paginas", "acercadepage", homepage.pk],
    )


def test_puede_crearse_y_persistirse(homepage):
    page = AcercaDePage(title="Acerca de", titulo="Acerca de la artista")
    homepage.add_child(instance=page)
    assert AcercaDePage.objects.filter(titulo="Acerca de la artista").exists()


def test_puede_guardar_texto(homepage, texto):
    page = AcercaDePage(
        title="Acerca de", titulo="Acerca de la artista", body=texto
    )
    homepage.add_child(instance=page)
    assert page.body == texto


def test_es_accesible_a_visitantes(site, acerca_de_page, client):
    response = client.get(acerca_de_page.url)
    assert response.status_code == 200


def test_url_de_creacion_es_accesible_a_usuarios_autenticados(
        authenticated_client, url_creacion):
    response = authenticated_client.get(url_creacion)
    assert response.status_code == 200


def test_puede_crearse_desde_el_admin_sin_error(authenticated_client, homepage):
    wagtailasserts.assert_can_create(
        homepage,
        AcercaDePage,
        nested_form_data({
            "title": "Acerca de",
            "titulo": "Acerca del artista",
            "body": rich_text("<p>Texto de prueba</p>")
        }),
        authenticated_client,
    )


def test_puede_ser_subpagina_de_homepage():
    wagtailasserts.assert_can_create_at(HomePage, AcercaDePage)
