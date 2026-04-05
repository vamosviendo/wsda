from wagtail.test.utils import WagtailPageTestCase

from produccion.models import AreaPage
from utils.test_utils import crear_estructura_basica


class AreaPageFunctionalTests(WagtailPageTestCase):
    """Verifica la experiencia del usuario en una página de área."""

    def setUp(self):
        _, self.homepage = crear_estructura_basica(self)
        self.area_page = AreaPage(
            title="Pintura",
            titulo="Pintura",
            descripcion="Obras realizadas en técnica pictórica.",
        )
        self.homepage.add_child(instance=self.area_page)

    def test_area_page_devuelve_200(self):
        response = self.client.get(self.area_page.url)
        self.assertEqual(response.status_code, 200)

    def test_area_page_usa_template_correcto(self):
        response = self.client.get(self.area_page.url)
        self.assertTemplateUsed(response, "produccion/area_page.html")

    def test_area_page_extiende_template_base(self):
        response = self.client.get(self.area_page.url)
        self.assertTemplateUsed(response, "base.html")

    def test_area_page_incluye_header(self):
        response = self.client.get(self.area_page.url)
        self.assertTemplateUsed(response, "includes/header.html")

    def test_area_page_incluye_footer(self):
        response = self.client.get(self.area_page.url)
        self.assertTemplateUsed(response, "includes/footer.html")

    def test_area_page_muestra_titulo(self):
        response = self.client.get(self.area_page.url)
        self.assertContains(response, "Pintura")

    def test_area_page_muestra_descripcion(self):
        response = self.client.get(self.area_page.url)
        self.assertContains(response, "Obras realizadas en técnica pictórica.")

    def test_area_page_tiene_grilla_de_productos(self):
        response = self.client.get(self.area_page.url)
        self.assertContains(response, 'class="productos-grid"')

    def test_area_page_sin_descripcion_se_renderiza(self):
        area_sin_desc = AreaPage(title="Escultura", titulo="Escultura")
        self.homepage.add_child(instance=area_sin_desc)
        response = self.client.get(area_sin_desc.url)
        self.assertEqual(response.status_code, 200)

    def test_area_page_muestra_nombre_del_sitio(self):
        response = self.client.get(self.area_page.url)
        self.assertContains(response, "Liliana Medela")

    def test_area_page_carga_css_del_area(self):
        response = self.client.get(self.area_page.url)
        self.assertContains(response, "area_page.css")

    def test_area_page_titulo_tiene_clase_correcta(self):
        response = self.client.get(self.area_page.url)
        self.assertContains(response, 'class="area-titulo"')
