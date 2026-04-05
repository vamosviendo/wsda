from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from home.models import HomePage
from produccion.models import AreaPage
from utils.test_utils import crear_estructura_basica


# ============================================================
# 1. TESTS FUNCIONALES — HomePage
# ============================================================

class HomePageFunctionalTests(WagtailPageTestCase):
    """
    Verifica la experiencia del usuario en la página de inicio.
    """

    def setUp(self):
        _, self.homepage = crear_estructura_basica(self)

    def test_homepage_devuelve_200(self):
        response = self.client.get(self.homepage.url)
        self.assertEqual(response.status_code, 200)

    def test_homepage_usa_template_home(self):
        response = self.client.get(self.homepage.url)
        self.assertTemplateUsed(response, "home/home_page.html")

    def test_homepage_extiende_template_base(self):
        response = self.client.get(self.homepage.url)
        self.assertTemplateUsed(response, "base.html")

    def test_homepage_tiene_contenedor_franjas(self):
        response = self.client.get(self.homepage.url)
        self.assertContains(response, 'class="franjas"')

    def test_homepage_titulo_presente(self):
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "Home")

    def test_area_aparece_en_nav_cuando_en_menu(self):
        area = AreaPage(title="Pintura", titulo="Pintura", show_in_menus=True)
        self.homepage.add_child(instance=area)
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "Pintura")

    def test_area_no_aparece_en_nav_cuando_no_en_menu(self):
        area = AreaPage(title="Oculta", titulo="Oculta", show_in_menus=False)
        self.homepage.add_child(instance=area)
        response = self.client.get(self.homepage.url)
        self.assertNotContains(response, "Oculta")


# ============================================================
# 2. TESTS UNITARIOS — HomePage.body
# ============================================================

class TestHomePageBody(WagtailPageTestCase):
    """Verifica el campo body de HomePage."""

    def setUp(self):
        self.root_page, self.homepage = crear_estructura_basica(self)

    def test_body_vacio_por_defecto(self):
        homepage = HomePage(title="Test vacío")
        self.root_page.add_child(instance=homepage)
        self.assertEqual(len(homepage.body), 0)

    def test_ruta_del_template(self):
        response = self.client.get(self.homepage.url)
        self.assertTemplateUsed(response, "home/home_page.html")
        self.assertTemplateNotUsed(response, "home/welcome_page.html")
