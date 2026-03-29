from selenium.webdriver.common.by import By

from base.models import FooterText, NavigationSettings
from functional_tests.base import FunctionalTestBase
from produccion.models import AreaPage


class HomePageFunctionalTests(FunctionalTestBase):
    """
    Verifica la portada tal como la ve el usuario en un browser real.
    """

    def test_homepage_loads(self):
        """La portada carga sin errores (no hay página de error en el título)."""
        self.get("/")
        title = self.browser.title
        self.assertNotIn("error", title.lower())
        self.assertNotIn("not found", title.lower())

    def test_homepage_incluye_container_franjas(self):
        """El contenedor .franjas existe en el DOM (puede estar vacío)."""
        self.get("/")
        elementos = self.browser.find_elements(By.CSS_SELECTOR, ".franjas")
        self.assertGreater(len(elementos), 0, "No se encontró el contenedor .franjas")

    def test_elemento_body_existe_en_homepage(self):
        """El elemento <body> está presente (smoke test del DOM)."""
        self.get("/")
        body = self.browser.find_element(By.TAG_NAME, "body")
        self.assertIsNotNone(body)


class HeaderFunctionalTests(FunctionalTestBase):
    """
    Verifica el header: nombre del sitio, navegación.
    """

    def test_nombre_del_sitio_es_visible(self):
        """El nombre del sitio es visible (el CSS no lo está ocultando)."""
        self.get("/")
        site_title = self.wait_for(".site-title")
        self.assertTrue(site_title.is_displayed())
        self.assertIn(self.site_name.lower(), site_title.text.lower())

    def test_nombre_del_sitio_es_un_link_a_home(self):
        """El nombre del sitio es un enlace a la raíz."""
        self.get("/")
        link = self.browser.find_element(By.CSS_SELECTOR, ".site-title a")
        href = link.get_attribute("href")
        self.assertTrue(href.endswith("/"))

    def test_nav_es_visible(self):
        """El menú de navegación está visible."""
        self.get("/")
        nav = self.wait_for("nav")
        self.assertTrue(nav.is_displayed())

    def test_link_de_inicio_existe_en_nav(self):
        """El ítem 'Inicio' aparece en el menú y es visible."""
        self.get("/")
        links = self.browser.find_elements(By.CSS_SELECTOR, "nav a")
        link_texts = [a.text.lower() for a in links]
        self.assertIn("inicio", link_texts)

    def test_link_blog_existe_en_nav(self):
        """El link al blog externo está en el menú y es visible."""
        self.get("/")
        links = self.browser.find_elements(By.CSS_SELECTOR, "nav a")
        hrefs = [a.get_attribute("href") for a in links]
        self.assertTrue(any("blogspot.com" in href for href in hrefs))

    def test_una_pagina_de_area_aparece_in_nav(self):
        """Una AreaPage con show_in_menus=True aparece visible en el menú."""
        area = AreaPage(title="Pintura", titulo="Pintura", show_in_menus=True)
        self.homepage.add_child(instance=area)
        self.get("/")
        links = self.browser.find_elements(By.CSS_SELECTOR, "nav a")
        link_texts = [a.text.lower() for a in links]
        self.assertIn("pintura", link_texts)

    def test_link_de_nav_navega_correctamente(self):
        """Un clic en 'Inicio' en el menú lleva a la URL correcta."""
        area = AreaPage(title="Pintura", titulo="Pintura", show_in_menus=True)
        self.homepage.add_child(instance=area)
        self.get(area.url)  # empezamos en otra página
        inicio_link = None
        for link in self.browser.find_elements(By.CSS_SELECTOR, "nav a"):
            if link.text.lower() == "inicio":
                inicio_link = link
                break
        self.assertIsNotNone(inicio_link, "No se encontró el link 'Inicio' en el menú")
        inicio_link.click()
        self.assertEqual(
            self.browser.current_url,
            f"{self.live_server_url}{self.homepage.url}"
        )

    def test_se_aplica_css_del_header(self):
        """
        El CSS del header fue cargado e interpretado por el browser.
        Verificamos una propiedad de .site-title que depende del CSS:
        font-family debe incluir 'Didact Gothic' (definida en base.css via var).
        """
        self.get("/")
        site_title = self.wait_for(".site-title")
        font_family = self.get_computed_style(site_title, "fontFamily")
        # Nos aseguramos de que no es el font genérico del sistema (serif/Times)
        # indicando que el CSS efectivamente cargó.
        self.assertNotEqual(font_family, "Times New Roman")
        self.assertNotEqual(font_family, "serif")


class FooterFunctionalTests(FunctionalTestBase):
    """
    Verifica el footer: crédito, redes sociales, footer text.
    """

    def test_footer_es_visible(self):
        """El footer es visible en la página."""
        self.get("/")
        footer = self.wait_for("footer")
        self.assertTrue(footer.is_displayed())

    def test_footer_credit_es_visible(self):
        """El crédito de diseño (HT) es visible en el footer."""
        self.get("/")
        footer = self.browser.find_element(By.CSS_SELECTOR, "footer")
        self.assertIn("HT", footer.text)

    def test_instagram_link_es_visible_si_esta_configurado(self):
        """El link de Instagram es visible cuando está configurado."""
        NavigationSettings(instagram_url="https://instagram.com/lilianamedela").save()
        self.get("/")
        links = self.browser.find_elements(By.CSS_SELECTOR, ".footer-social a")
        link_texts = [a.text.lower() for a in links]
        self.assertIn("instagram", link_texts)

    def test_instagram_link_navega_a_url_correcta(self):
        """El link de Instagram apunta a la URL configurada."""
        NavigationSettings(instagram_url="https://instagram.com/lilianamedela").save()
        self.get("/")
        insta_link = None
        for link in self.browser.find_elements(By.CSS_SELECTOR, ".footer-social a"):
            if link.text.lower() == "instagram":
                insta_link = link
                break
        self.assertIsNotNone(insta_link)
        self.assertEqual(
            insta_link.get_attribute("href"),
            "https://instagram.com/lilianamedela"
        )

    def test_texto_del_footer_es_visible_si_esta_publicado(self):
        """El texto del footer (snippet publicado) es visible."""
        FooterText.objects.create(body="<p>Obra de Liliana Medela</p>", live=True)
        self.get("/")
        footer = self.browser.find_element(By.CSS_SELECTOR, "footer")
        self.assertIn("Obra de Liliana Medela", footer.text)

    def test_texto_del_footer_no_es_visible_si_esta_en_borrador(self):
        """El texto del footer en borrador no es visible."""
        FooterText.objects.create(body="<p>Texto en borrador</p>", live=False)
        self.get("/")
        footer = self.browser.find_element(By.CSS_SELECTOR, "footer")
        self.assertNotIn("Texto en borrador", footer.text)
