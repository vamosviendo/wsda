"""
Tests para la app `base`.

Cubre:
  - NavigationSettings  (URLs de redes sociales)
  - GeneralSettings     (título del sitio)
  - FooterText          (snippet de texto de footer)
  - Template tags:      get_site_name, get_site_root, get_footer_text
  - Header              (renderizado funcional)
  - Footer              (renderizado funcional)

Organización:
  1. Tests funcionales: header y footer vistos por el usuario.
  2. Tests unitarios:   modelos y template tags.

Para correr solo estos tests:
  python manage.py test base
"""

from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from base.models import FooterText, GeneralSettings, NavigationSettings
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
    Los tests se ejecutan a través del renderizado de la homepage.
    """

    def setUp(self):
        self.site, self.homepage = crear_sitio_con_homepage("Liliana Medela")

    def test_header_renders_without_error(self):
        """El header se renderiza sin errores."""
        response = self.client.get(self.homepage.url)
        self.assertTemplateUsed(response, "includes/header.html")

    def test_header_shows_site_name(self):
        """El nombre del sitio (de Wagtail Site) aparece en el header."""
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "Liliana Medela")

    def test_header_site_name_has_correct_class(self):
        """El nombre del sitio tiene la clase CSS correcta."""
        response = self.client.get(self.homepage.url)
        self.assertContains(response, 'class="site-title"')

    def test_header_site_name_is_a_link(self):
        """El nombre del sitio es un enlace (a la raíz)."""
        response = self.client.get(self.homepage.url)
        self.assertContains(response, 'href="/"')

    def test_header_contains_nav_element(self):
        """El header contiene un elemento <nav> con los links del sitio."""
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "<nav>")

    def test_header_shows_inicio_link(self):
        """'Inicio' es siempre el primer ítem del menú."""
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "Inicio")

    def test_header_shows_blog_link(self):
        """El link al blog externo siempre está en el menú."""
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "lilianamedela.blogspot.com")

    def test_header_shows_area_page_in_menu_when_show_in_menus_true(self):
        """Una AreaPage con show_in_menus=True aparece en el menú."""
        area = AreaPage(title="Pintura", titulo="Pintura", show_in_menus=True)
        self.homepage.add_child(instance=area)
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "Pintura")

    def test_header_hides_area_page_in_menu_when_show_in_menus_false(self):
        """Una AreaPage con show_in_menus=False NO aparece en el menú."""
        area = AreaPage(title="Oculta", titulo="Oculta", show_in_menus=False)
        self.homepage.add_child(instance=area)
        response = self.client.get(self.homepage.url)
        self.assertNotContains(response, "Oculta")

    def test_header_loads_header_css(self):
        """La página carga el CSS del header."""
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "header.css")

    def test_header_is_present_on_area_page(self):
        """El header aparece también en las páginas de área (no solo en home)."""
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

    def test_footer_renders_without_error(self):
        """El footer se renderiza sin errores."""
        response = self.client.get(self.homepage.url)
        self.assertTemplateUsed(response, "includes/footer.html")

    def test_footer_element_is_present(self):
        """El elemento HTML <footer> está presente en la página."""
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "<footer>")

    def test_footer_contains_credit_link(self):
        """El crédito de diseño (HT) aparece en el footer."""
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "htejedor@gmail.com")

    def test_footer_shows_instagram_when_configured(self):
        """El link de Instagram aparece si está configurado en NavigationSettings."""
        NavigationSettings(instagram_url="https://instagram.com/lilianamedela").save()
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "Instagram")
        self.assertContains(response, "instagram.com/lilianamedela")

    def test_footer_shows_facebook_when_configured(self):
        """El link de Facebook aparece si está configurado."""
        NavigationSettings(facebook_url="https://facebook.com/lilianamedela").save()
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "Facebook")

    def test_footer_shows_x_when_configured(self):
        """El link de X aparece si está configurado."""
        NavigationSettings(x_url="https://x.com/lilianamedela").save()
        response = self.client.get(self.homepage.url)
        self.assertContains(response, ">X<")

    def test_footer_hides_instagram_when_not_configured(self):
        """El link de Instagram NO aparece si no está configurado."""
        response = self.client.get(self.homepage.url)
        self.assertNotContains(response, "Instagram")

    def test_footer_hides_facebook_when_not_configured(self):
        """El link de Facebook NO aparece si no está configurado."""
        response = self.client.get(self.homepage.url)
        self.assertNotContains(response, "Facebook")

    def test_footer_shows_footer_text_when_live(self):
        """El texto del footer (snippet) aparece cuando está publicado (live=True)."""
        FooterText.objects.create(body="<p>© 2025 Liliana Medela</p>", live=True)
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "© 2025 Liliana Medela")

    def test_footer_hides_footer_text_when_not_live(self):
        """El texto del footer no aparece si está en borrador (live=False)."""
        FooterText.objects.create(body="<p>Borrador</p>", live=False)
        response = self.client.get(self.homepage.url)
        self.assertNotContains(response, "Borrador")

    def test_footer_loads_footer_css(self):
        """La página carga el CSS del footer."""
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "footer.css")

    def test_footer_is_present_on_area_page(self):
        """El footer aparece también en las páginas internas."""
        area = AreaPage(title="Grabado", titulo="Grabado")
        self.homepage.add_child(instance=area)
        response = self.client.get(area.url)
        self.assertContains(response, "<footer>")


# ============================================================
# 3. TESTS UNITARIOS — NavigationSettings
# ============================================================

class NavigationSettingsTests(WagtailPageTestCase):
    """Verifica el modelo NavigationSettings."""

    def test_can_create_with_instagram_url(self):
        obj = NavigationSettings(instagram_url="https://instagram.com/test")
        obj.save()
        saved = NavigationSettings.objects.first()
        self.assertEqual(saved.instagram_url, "https://instagram.com/test")

    def test_can_create_with_facebook_url(self):
        obj = NavigationSettings(facebook_url="https://facebook.com/test")
        obj.save()
        saved = NavigationSettings.objects.first()
        self.assertEqual(saved.facebook_url, "https://facebook.com/test")

    def test_can_create_with_x_url(self):
        obj = NavigationSettings(x_url="https://x.com/test")
        obj.save()
        saved = NavigationSettings.objects.first()
        self.assertEqual(saved.x_url, "https://x.com/test")

    def test_can_create_with_all_urls(self):
        obj = NavigationSettings(
            instagram_url="https://instagram.com/test",
            facebook_url="https://facebook.com/test",
            x_url="https://x.com/test",
        )
        obj.save()
        saved = NavigationSettings.objects.first()
        self.assertEqual(saved.instagram_url, "https://instagram.com/test")
        self.assertEqual(saved.facebook_url, "https://facebook.com/test")
        self.assertEqual(saved.x_url, "https://x.com/test")

    def test_all_fields_are_optional(self):
        """NavigationSettings se puede guardar con todos los campos vacíos."""
        obj = NavigationSettings()
        obj.save()
        saved = NavigationSettings.objects.first()
        self.assertEqual(saved.instagram_url, "")
        self.assertEqual(saved.facebook_url, "")
        self.assertEqual(saved.x_url, "")


# ============================================================
# 4. TESTS UNITARIOS — GeneralSettings
# ============================================================

class GeneralSettingsTests(WagtailPageTestCase):
    """Verifica el modelo GeneralSettings."""

    def test_can_create_with_site_title(self):
        obj = GeneralSettings(site_title="Liliana Medela")
        obj.save()
        saved = GeneralSettings.objects.first()
        self.assertEqual(saved.site_title, "Liliana Medela")

    def test_site_title_is_optional(self):
        """El título del sitio puede estar vacío."""
        obj = GeneralSettings()
        obj.save()
        saved = GeneralSettings.objects.first()
        self.assertEqual(saved.site_title, "")

    def test_site_title_can_be_updated(self):
        obj = GeneralSettings(site_title="Título viejo")
        obj.save()
        obj.site_title = "Título nuevo"
        obj.save()
        self.assertEqual(GeneralSettings.objects.first().site_title, "Título nuevo")


# ============================================================
# 5. TESTS UNITARIOS — FooterText
# ============================================================

class FooterTextTests(WagtailPageTestCase):
    """Verifica el snippet FooterText."""

    def test_can_create_footer_text(self):
        """Se puede crear un FooterText con cuerpo HTML."""
        footer = FooterText(body="<p>© 2025</p>")
        footer.save()
        self.assertTrue(FooterText.objects.exists())

    def test_str_representation(self):
        """La representación en string es siempre 'Texto footer'."""
        footer = FooterText(body="<p>Cualquier texto</p>")
        footer.save()
        self.assertEqual(str(footer), "Texto footer")

    def test_live_is_true_by_default(self):
        """El FooterText recién creado está publicado (live=True) por defecto."""
        footer = FooterText(body="<p>Publicado</p>")
        footer.save()
        self.assertTrue(FooterText.objects.get(pk=footer.pk).live)

    def test_can_create_as_draft(self):
        """Se puede crear un FooterText como borrador (live=False)."""
        footer = FooterText(body="<p>Borrador</p>", live=False)
        footer.save()
        self.assertFalse(FooterText.objects.get(pk=footer.pk).live)

    def test_only_live_instance_shown_in_footer(self):
        """
        Si hay un borrador y una versión publicada, solo la publicada
        aparece en el footer.
        """
        _, homepage = crear_sitio_con_homepage()
        FooterText.objects.create(body="<p>Texto borrador</p>", live=False)
        FooterText.objects.create(body="<p>Texto publicado</p>", live=True)
        response = self.client.get(homepage.url)
        self.assertContains(response, "Texto publicado")
        self.assertNotContains(response, "Texto borrador")
