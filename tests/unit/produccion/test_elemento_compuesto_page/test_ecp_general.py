from pytest_django import asserts


def test_devuelve_200(elemento_compuesto, client):
    response = client.get(elemento_compuesto.url)
    assert response.status_code == 200


def test_usa_template_correcto(elemento_compuesto, client):
    response = client.get(elemento_compuesto.url)
    asserts.assertTemplateUsed(response, "produccion/elemento_compuesto_page.html")
