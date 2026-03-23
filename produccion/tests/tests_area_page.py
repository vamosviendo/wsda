from wagtail.test.utils import WagtailPageTestCase

from produccion.models import AreaPage
from produccion.tests.utils import crear_estructura_basica


# ============================================================
# 1. TESTS FUNCIONALES — AreaPage
# ============================================================

class AreaPageFunctionalTests(WagtailPageTestCase):
    """
    Verifica la experiencia del usuario en una página de área:
    la página que agrupa los productos (obras) de una categoría.
    """

    def setUp(self):
        _, self.homepage = crear_estructura_basica(self)
        self.area_page = AreaPage(
            title="Pintura",
            titulo="Pintura",
            descripcion="Obras realizadas en técnica pictórica.",
        )
        self.homepage.add_child(instance=self.area_page)

    # --- Acceso y respuesta HTTP ---

    def test_area_page_returns_200(self):
        """El usuario puede acceder a la página de área."""
        response = self.client.get(self.area_page.url)
        self.assertEqual(response.status_code, 200)

    # --- Templates ---

    def test_area_page_uses_correct_template(self):
        """La página de área usa su template específico."""
        response = self.client.get(self.area_page.url)
        self.assertTemplateUsed(response, "produccion/area_page.html")

    def test_area_page_extends_base_template(self):
        """La página de área hereda header, footer y estructura base."""
        response = self.client.get(self.area_page.url)
        self.assertTemplateUsed(response, "base.html")

    def test_area_page_includes_header(self):
        response = self.client.get(self.area_page.url)
        self.assertTemplateUsed(response, "includes/header.html")

    def test_area_page_includes_footer(self):
        response = self.client.get(self.area_page.url)
        self.assertTemplateUsed(response, "includes/footer.html")

    # --- Contenido visible ---

    def test_area_page_shows_titulo(self):
        """El título del área (campo `titulo`) es visible."""
        response = self.client.get(self.area_page.url)
        self.assertContains(response, "Pintura")

    def test_area_page_shows_descripcion(self):
        """La descripción del área es visible."""
        response = self.client.get(self.area_page.url)
        self.assertContains(response, "Obras realizadas en técnica pictórica.")

    def test_area_page_has_productos_grid(self):
        """La página tiene el contenedor de la grilla de productos."""
        response = self.client.get(self.area_page.url)
        self.assertContains(response, 'class="productos-grid"')

    def test_area_page_without_descripcion_still_renders(self):
        """La página funciona correctamente si no tiene descripción."""
        area_sin_desc = AreaPage(title="Escultura", titulo="Escultura")
        self.homepage.add_child(instance=area_sin_desc)
        response = self.client.get(area_sin_desc.url)
        self.assertEqual(response.status_code, 200)

    def test_area_page_shows_site_name_in_header(self):
        """El nombre del sitio aparece en el header de una página de área."""
        response = self.client.get(self.area_page.url)
        self.assertContains(response, "Liliana Medela")

    def test_area_page_loads_area_css(self):
        """La página carga el CSS específico de área."""
        response = self.client.get(self.area_page.url)
        self.assertContains(response, "area_page.css")

    def test_area_page_has_titulo_with_area_titulo_class(self):
        """El título tiene la clase CSS correcta."""
        response = self.client.get(self.area_page.url)
        self.assertContains(response, 'class="area-titulo"')


# ============================================================
# 2. TESTS UNITARIOS — AreaPage
# ============================================================

class AreaPageUnitTests(WagtailPageTestCase):
    """Verifica el modelo AreaPage: creación, campos, defaults."""

    def setUp(self):
        _, self.homepage = crear_estructura_basica(self)

    def test_area_page_can_be_created(self):
        """Se puede crear y persistir un AreaPage."""
        area = AreaPage(title="Test", titulo="Test")
        self.homepage.add_child(instance=area)
        self.assertTrue(AreaPage.objects.filter(titulo="Test").exists())

    def test_area_page_titulo_stored_correctly(self):
        """El campo `titulo` se guarda y recupera correctamente."""
        area = AreaPage(title="Grabado", titulo="Grabado")
        self.homepage.add_child(instance=area)
        retrieved = AreaPage.objects.get(titulo="Grabado")
        self.assertEqual(retrieved.titulo, "Grabado")

    def test_area_page_descripcion_optional(self):
        """El campo `descripcion` puede estar vacío."""
        area = AreaPage(title="Sin desc", titulo="Sin desc")
        self.homepage.add_child(instance=area)
        self.assertEqual(area.descripcion, "")

    def test_area_page_productos_empty_by_default(self):
        """El StreamField `productos` empieza vacío."""
        area = AreaPage(title="Vacía", titulo="Vacía")
        self.homepage.add_child(instance=area)
        self.assertEqual(len(area.productos), 0)

    def test_area_page_is_renderable(self):
        """Wagtail puede renderizar AreaPage sin errores."""
        area = AreaPage(title="Render test", titulo="Render test")
        self.homepage.add_child(instance=area)
        self.assertPageIsRenderable(area)
