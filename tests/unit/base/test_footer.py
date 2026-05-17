import pytest
from pytest_django import asserts

from base.models import FooterText, NavigationSettings


@pytest.fixture
def navigation_settings():
    return NavigationSettings.objects.get_or_create(pk=1)[0]


@pytest.fixture
def instagram_setting(navigation_settings):
    navigation_settings.instagram_url = "https://instagram.com/rogelioroldan"
    navigation_settings.save()


@pytest.fixture
def facebook_setting(navigation_settings):
    navigation_settings.facebook_url = "https://facebook.com/rogelioroldan"
    navigation_settings.save()


@pytest.fixture
def x_setting(navigation_settings):
    navigation_settings.x_url = "https://x.com/rogelioroldan"
    navigation_settings.save()


def test_se_usa_template_footer(site, homepage, client):
    response = client.get(homepage.url)
    asserts.assertTemplateUsed(response, "includes/footer.html")


@pytest.mark.parametrize("social", ["instagram", "facebook", "x"])
def test_pasa_url_de_redes_sociales_cuando_estan_configuradas(site, homepage, social, client, request):
    request.getfixturevalue(f"{social}_setting")
    url_attr = f"{social}_url"
    response = client.get(homepage.url)
    assert getattr(
        response.context["settings"]["base"]["navigationsettings"],
        url_attr
    ) == f"https://{social}.com/rogelioroldan"


@pytest.mark.parametrize("social", ["instagram", "facebook", "x"])
def test_no_pasa_url_de_redes_sociales_cuando_no_estan_configuradas(site, homepage, social, client):
    response = client.get(homepage.url)
    assert getattr(response.context["settings"]["base"]["navigationsettings"], f"{social}_url") == ""


def test_muestra_texto_cuando_publicado(site, homepage, client):
    FooterText.objects.create(body="<p>© Rogelio Roldán</p>")
    response = client.get(homepage.url)
    assert response.context["footer_text"] == "<p>© Rogelio Roldán</p>"


def test_oculta_texto_cuando_no_publicado(site, homepage, client):
    FooterText.objects.create(body="<p>Borrador</p>", live=False)
    response = client.get(homepage.url)
    assert response.context["footer_text"] == ""


def test_aparece_en_otras_paginas_ademas_de_home(site, area_page, client):
    response = client.get(area_page.url)
    asserts.assertTemplateUsed(response, "includes/footer.html")


def test_solo_muestra_texto_publicado(site, homepage, client):
    FooterText.objects.create(body="<p>© Rogelio Roldán</p>", live=True)
    FooterText.objects.create(body="<p>Borrador</p>", live=False)
    response = client.get(homepage.url)
    assert response.context["footer_text"] == "<p>© Rogelio Roldán</p>"
