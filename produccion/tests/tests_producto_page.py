from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from produccion.models import AreaPage, ElementoPage, ProductoPage
from utils.test_utils import crear_estructura_basica


Image = get_image_model()

# ============================================================
# 1. TESTS FUNCIONALES — ProductoPage
# ============================================================

class ProductoPageFunctionalTests(WagtailPageTestCase):
    """
    Verifica la experiencia del usuario en una página de producto:
    la galería de imágenes de una obra o serie.
    """

    def setUp(self):
        _, self.homepage = crear_estructura_basica(self)
        self.area_page = AreaPage(title="Pintura", titulo="Pintura")
        self.homepage.add_child(instance=self.area_page)
        self.producto_page = ProductoPage(
            title="Acrílicos sobre tela",
            titulo="Acrílicos sobre tela",
            descripcion="Serie de obras en acrílico sobre tela, 2023.",
        )
        self.area_page.add_child(instance=self.producto_page)

    # --- Acceso y respuesta HTTP ---

    def test_producto_page_returns_200(self):
        """El usuario puede acceder a la página de producto."""
        response = self.client.get(self.producto_page.url)
        self.assertEqual(response.status_code, 200)

    # --- Templates ---

    def test_producto_page_uses_correct_template(self):
        """La página de producto usa su template específico."""
        response = self.client.get(self.producto_page.url)
        self.assertTemplateUsed(response, "produccion/producto_page.html")

    def test_producto_page_extends_base_template(self):
        """La página de producto hereda el template base."""
        response = self.client.get(self.producto_page.url)
        self.assertTemplateUsed(response, "base.html")

    def test_producto_page_includes_header(self):
        response = self.client.get(self.producto_page.url)
        self.assertTemplateUsed(response, "includes/header.html")

    def test_producto_page_includes_footer(self):
        response = self.client.get(self.producto_page.url)
        self.assertTemplateUsed(response, "includes/footer.html")

    # --- Contenido visible ---

    def test_producto_page_shows_titulo(self):
        """El título del producto es visible."""
        response = self.client.get(self.producto_page.url)
        self.assertContains(response, "Acrílicos sobre tela")

    def test_producto_page_shows_descripcion(self):
        """La descripción introductoria del producto es visible."""
        response = self.client.get(self.producto_page.url)
        self.assertContains(response, "Serie de obras en acrílico sobre tela, 2023.")

    def test_producto_page_has_imagenes_grid(self):
        """La página tiene el contenedor de la galería de imágenes."""
        response = self.client.get(self.producto_page.url)
        self.assertContains(response, 'class="imagenes-grid"')

    def test_producto_page_without_descripcion_still_renders(self):
        """La página funciona si no tiene descripción."""
        producto_sin_desc = ProductoPage(title="Sin descripción", titulo="Sin descripción")
        self.area_page.add_child(instance=producto_sin_desc)
        response = self.client.get(producto_sin_desc.url)
        self.assertEqual(response.status_code, 200)

    def test_producto_page_loads_producto_css(self):
        """La página carga el CSS específico de producto."""
        response = self.client.get(self.producto_page.url)
        self.assertContains(response, "producto_page.css")

    def test_producto_page_has_titulo_with_producto_titulo_class(self):
        """El título tiene la clase CSS correcta."""
        response = self.client.get(self.producto_page.url)
        self.assertContains(response, 'class="producto-titulo"')

    def test_producto_page_descripcion_has_pagina_descripcion_class(self):
        """La descripción de página tiene la clase CSS correcta (no confundir con .producto-descripcion)."""
        response = self.client.get(self.producto_page.url)
        self.assertContains(response, 'class="pagina-descripcion"')


# ============================================================
# 2. TESTS UNITARIOS — ProductoPage
# ============================================================

class ProductoPageUnitTests(WagtailPageTestCase):
    """Verifica el modelo ProductoPage: creación, campos, defaults."""

    def setUp(self):
        _, self.homepage = crear_estructura_basica(self)
        self.area_page = AreaPage(title="Pintura", titulo="Pintura")
        self.homepage.add_child(instance=self.area_page)

    def test_producto_page_can_be_created(self):
        """Se puede crear y persistir un ProductoPage."""
        producto = ProductoPage(title="Test", titulo="Test")
        self.area_page.add_child(instance=producto)
        self.assertTrue(ProductoPage.objects.filter(titulo="Test").exists())

    def test_producto_page_titulo_stored_correctly(self):
        """El campo `titulo` se guarda y recupera correctamente."""
        producto = ProductoPage(title="Óleos", titulo="Óleos")
        self.area_page.add_child(instance=producto)
        retrieved = ProductoPage.objects.get(titulo="Óleos")
        self.assertEqual(retrieved.titulo, "Óleos")

    def test_producto_page_descripcion_optional(self):
        """El campo `descripcion` puede estar vacío."""
        producto = ProductoPage(title="Sin desc", titulo="Sin desc")
        self.area_page.add_child(instance=producto)
        self.assertEqual(producto.descripcion, "")

    def test_producto_page_is_renderable(self):
        """Wagtail puede renderizar ProductoPage sin errores."""
        producto = ProductoPage(title="Render test", titulo="Render test")
        self.area_page.add_child(instance=producto)
        self.assertPageIsRenderable(producto)

# ============================================================
# 3. TESTS DE LA GALERÍA DE IMÁGENES — ProductoPage
# ============================================================

class ProductoPageOrdenGaleriaTests(WagtailPageTestCase):

    def setUp(self):
        root_page = Page.get_first_root_node()
        Site.objects.create(
            hostname="testsite", root_page=root_page, is_default_site=True
        )
        area = AreaPage(title="Área test", titulo="Área test")
        root_page.add_child(instance=area)

        self.producto = ProductoPage(title="Producto test", titulo="Producto test")
        area.add_child(instance=self.producto)

        self.imagen = Image.objects.create(
            title="Test image", file=get_test_image_file()
        )

        self.e1 = ElementoPage(title="Primero", slug="primero", imagen=self.imagen)
        self.producto.add_child(instance=self.e1)

        self.e2 = ElementoPage(title="Segundo", slug="segundo", imagen=self.imagen)
        self.producto.add_child(instance=self.e2)

        self.e3 = ElementoPage(title="Tercero", slug="tercero", imagen=self.imagen)
        self.producto.add_child(instance=self.e3)

    def test_galeria_respeta_orden_del_arbol(self):
        """El orden de elementos en la galería refleja el orden del árbol de páginas."""
        response = self.client.get(self.producto.url)
        content = response.content.decode()
        pos1 = content.index(self.e1.url)
        pos2 = content.index(self.e2.url)
        pos3 = content.index(self.e3.url)
        self.assertLess(pos1, pos2)
        self.assertLess(pos2, pos3)

    def test_galeria_respeta_orden_modificado(self):
        """Si se modifica el orden del árbol, la galería lo refleja."""
        # Mover e3 antes de e1 usando la API de treebeard
        self.e3.move(self.e1, pos="left")

        response = self.client.get(self.producto.url)
        content = response.content.decode()
        pos3 = content.index(self.e3.url)
        pos1 = content.index(self.e1.url)
        self.assertLess(pos3, pos1)


class ProductoPageMetAnteriorSiguiente(WagtailPageTestCase):
    def setUp(self):
        root_page = Page.get_first_root_node()
        Site.objects.create(
            hostname="testsite", root_page=root_page, is_default_site=True
        )
        area = AreaPage(title="Área test", titulo="Área test")
        root_page.add_child(instance=area)

        self.producto1 = ProductoPage(title="Producto 1", titulo="Producto uno")
        area.add_child(instance=self.producto1)

        self.producto2 = ProductoPage(title="Producto 2", titulo="Producto dos")
        area.add_child(instance=self.producto2)

        self.producto3 = ProductoPage(title="Producto 3", titulo="Producto tres")
        area.add_child(instance=self.producto3)

    def test_get_producto_anterior_devuelve_pagina_de_producto_anterior(self):
        self.assertEqual(self.producto2.get_producto_anterior(), self.producto1)

    def test_get_producto_anterior_devuelve_None_si_no_hay_producto_anterior(self):
        self.assertIsNone(self.producto1.get_producto_anterior())

    def test_get_producto_siguiente_devuelve_pagina_de_producto_siguiente(self):
        self.assertEqual(self.producto2.get_producto_siguiente(), self.producto3)

    def test_get_producto_siguiente_devuelve_None_si_no_hay_producto_siguiente(self):
        self.assertIsNone(self.producto3.get_producto_siguiente())
