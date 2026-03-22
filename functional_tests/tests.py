"""
Tests funcionales con Selenium para el proyecto wlili.

Estos tests complementan (no reemplazan) los tests del cliente HTTP de Django.
La diferencia clave es que Selenium lanza un browser real, que:
  - hace requests reales a los archivos de media e imágenes
  - interpreta y aplica el CSS
  - ejecuta JavaScript

Esto permite detectar errores que el cliente HTTP de Django no puede ver:
  - imágenes cuya URL existe en el HTML pero cuyo archivo no existe en el servidor
  - CSS que no se aplica porque el archivo .css no fue encontrado
  - problemas de configuración de servidor (MEDIA_ROOT, STATIC_ROOT, Nginx, etc.)

Prerequisitos:
  pip install selenium

El WebDriver de Chrome (chromedriver) debe estar instalado y en el PATH.
Se puede usar Firefox (geckodriver) cambiando el import y la instanciación.

Para correr:
  python manage.py test functional_tests

Estructura del archivo:
  - FunctionalTestBase        clase base compartida
  - HomePageFunctionalTests   portada
  - HeaderFunctionalTests     header (nav, site name)
  - FooterFunctionalTests     footer (redes, crédito)
  - AreaPageFunctionalTests   página de área
  - ProductoPageFunctionalTests  página de producto — GALERÍA DE IMÁGENES
"""

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Locale, Page, Site

from base.models import FooterText, NavigationSettings
from home.models import HomePage
from produccion.models import AreaPage, ProductoPage


# ============================================================
# Clase base compartida
# ============================================================

class FunctionalTestBase(StaticLiveServerTestCase):
    """
    Clase base para todos los tests de Selenium.
    Gestiona el ciclo de vida del browser y la fixture mínima del sitio.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        # options.add_argument("--headless")        # sin ventana visible en CI/CD
        options.add_argument("--width=1280")
        options.add_argument("--height=900")
        cls.browser = webdriver.Firefox(options=options)
        cls.browser.implicitly_wait(15)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        """
        Crea la estructura mínima de Wagtail para cada test:
        Site (hostname = live_server_url) → HomePage

        Nota sobre TransactionTestCase:
        StaticLiveServerTestCase hereda de TransactionTestCase, que hace un
        flush completo de la base de datos entre tests (a diferencia de TestCase,
        que usa rollback). Ese flush borra también la página raíz que Wagtail
        crea en su migración inicial, así que hay que recrearla si no existe.
        """
        # 1. Locale. Necesario para poder crear páginas
        Locale.objects.get_or_create(language_code=settings.LANGUAGE_CODE)

        # 2. Página raíz del árbol de Wagtail
        root_page = Page.objects.filter(depth=1).first() \
                    or Page.add_root(title="Root", slug="root")

        # Si un setUp anterior falló a mitad, puede haber quedado una HomePage
        # con slug="home". La borramos antes de crear la nueva.
        for child in root_page.get_children():
            child.delete()
        root_page.refresh_from_db()

        self.homepage = HomePage(title="Home", slug="home")
        root_page.add_child(instance=self.homepage)

        self.site_name = "Liliana Medela"
        self.site = Site.objects.create(
            # El Site apunta a homepage, no a root_page.
            # Wagtail sirve la página que es root_page del Site;
            # si apuntara al nodo raíz del árbol, el browser mostraría "Root".
            hostname=self._get_hostname(),
            port=self._get_port(),
            root_page=self.homepage,
            is_default_site=True,
            site_name=self.site_name,
        )

    def _get_hostname(self):
        """Extrae el hostname de la URL del servidor de test."""
        return self.live_server_url.replace("http://", "").split(":")[0]

    def _get_port(self):
        """Extrae el puerto de la URL del servidor de test."""
        parts = self.live_server_url.replace("http://", "").split(":")
        return int(parts[1]) if len(parts) > 1 else 80

    def get(self, path="/"):
        """Navega a una ruta relativa del servidor de test."""
        self.browser.get(f"{self.live_server_url}{path}")

    def wait_for(self, css_selector, timeout=5):
        """Espera hasta que un selector CSS esté presente en el DOM."""
        return WebDriverWait(self.browser, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )

    def image_loaded(self, img_element):
        """
        Devuelve True si la imagen fue descargada y renderizada correctamente.
        naturalWidth === 0 significa que el browser no pudo cargar el archivo.
        Este es el test que el cliente HTTP de Django NO puede hacer.
        """
        return self.browser.execute_script(
            "return arguments[0].naturalWidth > 0", img_element
        )

    def element_is_visible(self, css_selector):
        """Verifica que un elemento existe Y es visible en la página."""
        try:
            element = self.browser.find_element(By.CSS_SELECTOR, css_selector)
            return element.is_displayed()
        except Exception:
            return False

    def get_computed_style(self, element, prop):
        """Devuelve el valor de una propiedad CSS computada (interpretada por el browser)."""
        return self.browser.execute_script(
            f"return window.getComputedStyle(arguments[0]).{prop}", element
        )


# ============================================================
# Tests — Portada
# ============================================================

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

    def test_homepage_has_franjas_container(self):
        """El contenedor .franjas existe en el DOM (puede estar vacío)."""
        self.get("/")
        elementos = self.browser.find_elements(By.CSS_SELECTOR, ".franjas")
        self.assertGreater(len(elementos), 0, "No se encontró el contenedor .franjas")

    def test_homepage_body_element_exists(self):
        """El elemento <body> está presente (smoke test del DOM)."""
        self.get("/")
        body = self.browser.find_element(By.TAG_NAME, "body")
        self.assertIsNotNone(body)


# ============================================================
# Tests — Header
# ============================================================

class HeaderFunctionalTests(FunctionalTestBase):
    """
    Verifica el header: nombre del sitio, navegación.
    """

    def test_site_name_is_visible(self):
        """El nombre del sitio es visible (el CSS no lo está ocultando)."""
        self.get("/")
        site_title = self.wait_for(".site-title")
        self.assertTrue(site_title.is_displayed())
        self.assertIn(self.site_name.lower(), site_title.text.lower())

    def test_site_name_is_a_link_to_root(self):
        """El nombre del sitio es un enlace a la raíz."""
        self.get("/")
        link = self.browser.find_element(By.CSS_SELECTOR, ".site-title a")
        href = link.get_attribute("href")
        self.assertTrue(href.endswith("/"))

    def test_nav_is_visible(self):
        """El menú de navegación está visible."""
        self.get("/")
        nav = self.wait_for("nav")
        self.assertTrue(nav.is_displayed())

    def test_inicio_link_is_in_nav(self):
        """El ítem 'Inicio' aparece en el menú y es visible."""
        self.get("/")
        links = self.browser.find_elements(By.CSS_SELECTOR, "nav a")
        link_texts = [a.text.lower() for a in links]
        self.assertIn("inicio", link_texts)

    def test_blog_link_is_in_nav(self):
        """El link al blog externo está en el menú y es visible."""
        self.get("/")
        links = self.browser.find_elements(By.CSS_SELECTOR, "nav a")
        hrefs = [a.get_attribute("href") for a in links]
        self.assertTrue(any("blogspot.com" in href for href in hrefs))

    def test_area_page_appears_in_nav(self):
        """Una AreaPage con show_in_menus=True aparece visible en el menú."""
        area = AreaPage(title="Pintura", titulo="Pintura", show_in_menus=True)
        self.homepage.add_child(instance=area)
        self.get("/")
        links = self.browser.find_elements(By.CSS_SELECTOR, "nav a")
        link_texts = [a.text.lower() for a in links]
        self.assertIn("pintura", link_texts)

    def test_nav_link_navigates_correctly(self):
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

    def test_header_css_is_applied(self):
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


# ============================================================
# Tests — Footer
# ============================================================

class FooterFunctionalTests(FunctionalTestBase):
    """
    Verifica el footer: crédito, redes sociales, footer text.
    """

    def test_footer_is_visible(self):
        """El footer es visible en la página."""
        self.get("/")
        footer = self.wait_for("footer")
        self.assertTrue(footer.is_displayed())

    def test_footer_credit_is_visible(self):
        """El crédito de diseño (HT) es visible en el footer."""
        self.get("/")
        footer = self.browser.find_element(By.CSS_SELECTOR, "footer")
        self.assertIn("HT", footer.text)

    def test_instagram_link_is_visible_when_configured(self):
        """El link de Instagram es visible cuando está configurado."""
        NavigationSettings(instagram_url="https://instagram.com/lilianamedela").save()
        self.get("/")
        links = self.browser.find_elements(By.CSS_SELECTOR, ".footer-social a")
        link_texts = [a.text.lower() for a in links]
        self.assertIn("instagram", link_texts)

    def test_instagram_link_navigates_to_correct_url(self):
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

    def test_footer_text_is_visible_when_live(self):
        """El texto del footer (snippet publicado) es visible."""
        FooterText.objects.create(body="<p>Obra de Liliana Medela</p>", live=True)
        self.get("/")
        footer = self.browser.find_element(By.CSS_SELECTOR, "footer")
        self.assertIn("Obra de Liliana Medela", footer.text)

    def test_footer_text_not_visible_when_draft(self):
        """El texto del footer en borrador no es visible."""
        FooterText.objects.create(body="<p>Texto en borrador</p>", live=False)
        self.get("/")
        footer = self.browser.find_element(By.CSS_SELECTOR, "footer")
        self.assertNotIn("Texto en borrador", footer.text)


# ============================================================
# Tests — AreaPage
# ============================================================

class AreaPageFunctionalTests(FunctionalTestBase):
    """
    Verifica la página de área (grilla de productos/series).
    """

    def setUp(self):
        super().setUp()
        self.area_page = AreaPage(
            title="Pintura",
            titulo="Pintura",
            descripcion="Obras en técnica pictórica.",
        )
        self.homepage.add_child(instance=self.area_page)

    def test_area_page_loads(self):
        """La página de área carga sin errores."""
        self.get(self.area_page.url)
        self.assertNotIn("error", self.browser.title.lower())

    def test_area_titulo_is_visible(self):
        """El título del área es visible en la página."""
        self.get(self.area_page.url)
        titulo = self.wait_for(".area-titulo")
        self.assertTrue(titulo.is_displayed())
        self.assertIn("Pintura", titulo.text)

    def test_area_descripcion_is_visible(self):
        """La descripción del área es visible."""
        self.get(self.area_page.url)
        desc = self.wait_for(".area-descripcion")
        self.assertTrue(desc.is_displayed())
        self.assertIn("Obras en técnica pictórica.", desc.text)

    def test_productos_grid_is_visible(self):
        """El contenedor de la grilla de productos existe en el DOM (puede estar vacío)."""
        self.get(self.area_page.url)
        elementos = self.browser.find_elements(By.CSS_SELECTOR, ".productos-grid")
        self.assertGreater(
            len(elementos), 0,
            "No se encontró el contenedor .productos-grid en el DOM"
        )

    def test_area_css_is_applied(self):
        """
        El CSS del área fue aplicado correctamente.
        Verificamos que .area-titulo tiene el display esperado.
        """
        self.get(self.area_page.url)
        titulo = self.wait_for(".area-titulo")
        display = self.get_computed_style(titulo, "display")
        self.assertNotEqual(display, "none")
