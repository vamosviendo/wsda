from pytest_django import asserts
from wagtail.models import Page


def test_se_usa_template_header(site, homepage, client):
    response = client.get(homepage.url)
    asserts.assertTemplateUsed(response, "includes/header.html")


def test_muestra_nombre_del_sitio(site, homepage, client):
    response = client.get(homepage.url)
    assert response.context["site_name"] == site.site_name


def test_pasa_raiz_del_sitio(site, homepage, client):
    response = client.get(homepage.url)
    assert response.context["site_root"] == Page.objects.get(pk=homepage.pk)


def test_aparece_en_paginas_distintas_de_home(site, area_page, client):
    response = client.get(area_page.url)
    asserts.assertTemplateUsed(response, "includes/header.html")