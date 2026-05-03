from pytest_django import asserts


def test_devuelve_200(site, homepage, client):
    response = client.get(homepage.url)
    assert response.status_code == 200


def test_usa_template_home(site, homepage, client):
    response = client.get(homepage.url)
    asserts.assertTemplateUsed(response, "home/home_page.html")
