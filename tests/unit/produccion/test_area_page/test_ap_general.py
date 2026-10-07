from pytest_django import asserts


def test_devuelve_200(area_page, client):
    response = client.get(area_page.url)
    assert response.status_code == 200


def test_usa_template_correcto(area_page, client):
    response = client.get(area_page.url)
    asserts.assertTemplateUsed(response, "produccion/area_page.html")
