from pytest_django import asserts


def test_devuelve_200(producto_page, client):
    response = client.get(producto_page.url)
    assert response.status_code == 200


def test_usa_template_correcto(producto_page, client):
    response = client.get(producto_page.url)
    asserts.assertTemplateUsed(response, "produccion/producto_page.html")
