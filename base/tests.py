"""
Tests para la app `base`.

Cubre:
  - Header y Footer (tests funcionales)
  - FooterText modelo (__str__, get_preview_context)
  - Template tag get_footer_text

Para correr solo estos tests:
  pytest base/tests.py
"""

from django.test import RequestFactory
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from base.models import FooterText, GeneralSettings, NavigationSettings
from base.templatetags.navigation_tags import get_footer_text
from home.models import HomePage
from produccion.models import AreaPage


# ============================================================
# Fixture compartida
# ============================================================

def crear_sitio_con_homepage(site_name="Liliana Medela"):
    """
    Crea la estructura mínima: site + homepage.
    Devuelve (site, homepage).
    """
    root_page = Page.get_first_root_node()
    homepage = HomePage(title="Home")
    root_page.add_child(instance=homepage)
    site = Site.objects.create(
        hostname="testsite",
        root_page=homepage,
        is_default_site=True,
        site_name=site_name,
    )
    return site, homepage


# ============================================================
# 1. TESTS FUNCIONALES — Header
# ============================================================

class HeaderFunctionalTests(WagtailPageTestCase):
    """
    Verifica el comportamiento del header tal como lo ve el usuario.
    """

    def setUp(self):
        self.site, self.homepage = crear_sitio_con_homepage("Liliana Medela")

    def test_header_se_renderiza_sin_error(self):
        response = self.client.get(self.homepage.url)
        self.assertTemplateUsed(response, "includes/header.html")

    def test_header_muestra_nombre_del_sitio(self):
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "Liliana Medela")

    def test_header_nombre_del_sitio_tiene_clase_correcta(self):
        response = self.client.get(self.homepage.url)
        self.assertContains(response, 'class="site-title"')

    def test_header_nombre_del_sitio_es_enlace(self):
        response = self.client.get(self.homepage.url)
        self.assertContains(response, 'href="/"')

    def test_header_contiene_elemento_nav(self):
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "<nav>")

    def test_header_muestra_enlace_inicio(self):
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "Inicio")

    def test_header_muestra_enlace_blog(self):
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "lilianamedela.blogspot.com")

    def test_header_muestra_area_en_menu_cuando_show_in_menus_es_true(self):
        area = AreaPage(title="Pintura", titulo="Pintura", show_in_menus=True)
        self.homepage.add_child(instance=area)
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "Pintura")

    def test_header_oculta_area_en_menu_cuando_show_in_menus_es_false(self):
        area = AreaPage(title="Oculta", titulo="Oculta", show_in_menus=False)
        self.homepage.add_child(instance=area)
        response = self.client.get(self.homepage.url)
        self.assertNotContains(response, "Oculta")

    def test_header_carga_css_del_header(self):
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "header.css")

    def test_header_aparece_en_pagina_de_area(self):
        area = AreaPage(title="Grabado", titulo="Grabado")
        self.homepage.add_child(instance=area)
        response = self.client.get(area.url)
        self.assertContains(response, "Liliana Medela")


# ============================================================
# 2. TESTS FUNCIONALES — Footer
# ============================================================

class FooterFunctionalTests(WagtailPageTestCase):
    """
    Verifica el comportamiento del footer tal como lo ve el usuario.
    """

    def setUp(self):
        _, self.homepage = crear_sitio_con_homepage()

    def test_footer_se_renderiza_sin_error(self):
        response = self.client.get(self.homepage.url)
        self.assertTemplateUsed(response, "includes/footer.html")

    def test_footer_elemento_presente(self):
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "<footer>")

    def test_footer_contiene_enlace_de_credito(self):
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "htejedor@gmail.com")

    def test_footer_muestra_instagram_cuando_configurado(self):
        settings, _ = NavigationSettings.objects.get_or_create(pk=1)
        settings.instagram_url = "https://instagram.com/lilianamedela"
        settings.save()
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "Instagram")
        self.assertContains(response, "instagram.com/lilianamedela")

    def test_footer_muestra_facebook_cuando_configurado(self):
        settings, _ = NavigationSettings.objects.get_or_create(pk=1)
        settings.facebook_url = "https://facebook.com/lilianamedela"
        settings.save()
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "Facebook")

    def test_footer_muestra_x_cuando_configurado(self):
        settings, _ = NavigationSettings.objects.get_or_create(pk=1)
        settings.x_url = "https://x.com/lilianamedela"
        settings.save()
        response = self.client.get(self.homepage.url)
        self.assertContains(response, ">X<")

    def test_footer_oculta_instagram_cuando_no_configurado(self):
        response = self.client.get(self.homepage.url)
        self.assertNotContains(response, "Instagram")

    def test_footer_oculta_facebook_cuando_no_configurado(self):
        response = self.client.get(self.homepage.url)
        self.assertNotContains(response, "Facebook")

    def test_footer_muestra_texto_cuando_publicado(self):
        FooterText.objects.create(body="<p>© 2025 Liliana Medela</p>", live=True)
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "© 2025 Liliana Medela")

    def test_footer_oculta_texto_cuando_borrador(self):
        FooterText.objects.create(body="<p>Borrador</p>", live=False)
        response = self.client.get(self.homepage.url)
        self.assertNotContains(response, "Borrador")

    def test_footer_carga_css_del_footer(self):
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "footer.css")

    def test_footer_aparece_en_pagina_de_area(self):
        area = AreaPage(title="Grabado", titulo="Grabado")
        self.homepage.add_child(instance=area)
        response = self.client.get(area.url)
        self.assertContains(response, "<footer>")

    def test_solo_muestra_texto_publicado(self):
        """Si hay borrador y versión publicada, solo la publicada aparece."""
        FooterText.objects.create(body="<p>Texto borrador</p>", live=False)
        FooterText.objects.create(body="<p>Texto publicado</p>", live=True)
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "Texto publicado")
        self.assertNotContains(response, "Texto borrador")


# ============================================================
# 3. TESTS UNITARIOS — FooterText.__str__
# ============================================================

class TestFooterTextStr(WagtailPageTestCase):
    """Verifica FooterText.__str__."""

    def test_devuelve_texto_footer(self):
        footer = FooterText(body="<p>Cualquier texto</p>")
        footer.save()
        self.assertEqual(str(footer), "Texto footer")


# ============================================================
# 4. TESTS UNITARIOS — FooterText.get_preview_context
# ============================================================

class TestFooterTextGetPreviewContext(WagtailPageTestCase):
    """Verifica FooterText.get_preview_context."""

    def test_devuelve_context_con_footer_text(self):
        footer = FooterText(body="<p>Vista previa</p>")
        footer.save()
        factory = RequestFactory()
        request = factory.get("/")
        context = footer.get_preview_context(request, "")
        self.assertEqual(context["footer_text"], "<p>Vista previa</p>")


# ============================================================
# 5. TESTS UNITARIOS — Template tag get_footer_text
# ============================================================

class TestGetFooterText(WagtailPageTestCase):
    """Verifica el template tag get_footer_text."""

    def test_usa_footer_text_de_context_si_existe(self):
        result = get_footer_text({"footer_text": "<p>Desde context</p>"})
        self.assertEqual(result["footer_text"], "<p>Desde context</p>")

    def test_consulta_db_si_context_no_tiene_footer_text(self):
        FooterText.objects.create(body="<p>Desde DB</p>", live=True)
        result = get_footer_text({})
        self.assertEqual(result["footer_text"], "<p>Desde DB</p>")

    def test_devuelve_vacio_si_no_hay_footer_text_live(self):
        FooterText.objects.create(body="<p>Borrador</p>", live=False)
        result = get_footer_text({})
        self.assertEqual(result["footer_text"], "")
