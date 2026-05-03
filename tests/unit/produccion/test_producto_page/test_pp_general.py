import pytest
from pytest_django import asserts

from produccion.models import ElementoPage


@pytest.fixture
def elemento_2(test_page, producto_page, objeto_imagen):
    return test_page(
        parent=producto_page,
        page_type=ElementoPage,
        title="Segundo elemento",
        slug="segundo",
        imagen=objeto_imagen,
        alt_imagen="Imagen de segundo elemento",
    )


@pytest.fixture
def elemento_3(test_page, producto_page, objeto_imagen):
    return test_page(
        parent=producto_page,
        page_type=ElementoPage,
        title="Tercer elemento",
        slug="tercero",
        imagen=objeto_imagen,
        alt_imagen="Imagen de tercer elemento",
    )


def test_devuelve_200(producto_page, client):
    response = client.get(producto_page.url)
    assert response.status_code == 200


def test_usa_template_correcto(producto_page, client):
    response = client.get(producto_page.url)
    asserts.assertTemplateUsed(response, "produccion/producto_page.html")


def test_galeria_incluye_elementos_hijos(producto_page, elemento, client):
    response = client.get(producto_page.url)
    assert list(response.context["elementos"]) == [elemento]


def test_galeria_respeta_orden_del_arbol(
        producto_page, elemento, elemento_2, elemento_3, client):
    response = client.get(producto_page.url)
    assert list(response.context["elementos"]) == [elemento, elemento_2, elemento_3]


def test_galeria_respeta_orden_modificado(
        producto_page, elemento, elemento_2, elemento_3, client):
    elemento_3.move(elemento, pos="left")
    response = client.get(producto_page.url)
    assert list(response.context["elementos"]) == [elemento_3, elemento, elemento_2]
