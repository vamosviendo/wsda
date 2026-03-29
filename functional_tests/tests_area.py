from selenium.webdriver.common.by import By

from functional_tests.base import FunctionalTestBase
from produccion.models import AreaPage


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

    def test_area_page_carga(self):
        """La página de área carga sin errores."""
        self.get(self.area_page.url)
        self.assertNotIn("error", self.browser.title.lower())

    def test_area_titulo_es_visible(self):
        """El título del área es visible en la página."""
        self.get(self.area_page.url)
        titulo = self.wait_for(".area-titulo")
        self.assertTrue(titulo.is_displayed())
        self.assertIn("Pintura", titulo.text)

    def test_area_descripcion_es_visible(self):
        """La descripción del área es visible."""
        self.get(self.area_page.url)
        desc = self.wait_for(".area-descripcion")
        self.assertTrue(desc.is_displayed())
        self.assertIn("Obras en técnica pictórica.", desc.text)

    def test_productos_grid_es_visible(self):
        """El contenedor de la grilla de productos existe en el DOM (puede estar vacío)."""
        self.get(self.area_page.url)
        elementos = self.browser.find_elements(By.CSS_SELECTOR, ".productos-grid")
        self.assertGreater(
            len(elementos), 0,
            "No se encontró el contenedor .productos-grid en el DOM"
        )

    def test_area_css_se_aplica(self):
        """
        El CSS del área fue aplicado correctamente.
        Verificamos que .area-titulo tiene el display esperado.
        """
        self.get(self.area_page.url)
        titulo = self.wait_for(".area-titulo")
        display = self.get_computed_style(titulo, "display")
        self.assertNotEqual(display, "none")
