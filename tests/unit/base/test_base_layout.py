from pytest_django import asserts


def test_base_carga_css_base(site, homepage, client):
    response = client.get(homepage.url)
    asserts.assertContains(response, "base.css")
