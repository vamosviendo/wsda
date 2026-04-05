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
    """Verifica la experiencia del usuario en una página de producto."""

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

    def test_producto_page_devuelve_200(self):
        response = self.client.get(self.producto_page.url)
        self.assertEqual(response.status_code, 200)

    def test_producto_page_usa_template_correcto(self):
        response = self.client.get(self.producto_page.url)
        self.assertTemplateUsed(response, "produccion/producto_page.html")

    def test_producto_page_extiende_template_base(self):
        response = self.client.get(self.producto_page.url)
        self.assertTemplateUsed(response, "base.html")

    def test_producto_page_incluye_header(self):
        response = self.client.get(self.producto_page.url)
        self.assertTemplateUsed(response, "includes/header.html")

    def test_producto_page_incluye_footer(self):
        response = self.client.get(self.producto_page.url)
        self.assertTemplateUsed(response, "includes/footer.html")

    def test_producto_page_muestra_titulo(self):
        response = self.client.get(self.producto_page.url)
        self.assertContains(response, "Acrílicos sobre tela")

    def test_producto_page_muestra_descripcion(self):
        response = self.client.get(self.producto_page.url)
        self.assertContains(response, "Serie de obras en acrílico sobre tela, 2023.")

    def test_producto_page_tiene_grilla_de_imagenes(self):
        response = self.client.get(self.producto_page.url)
        self.assertContains(response, 'class="imagenes-grid"')

    def test_producto_page_sin_descripcion_se_renderiza(self):
        producto_sin_desc = ProductoPage(title="Sin descripción", titulo="Sin descripción")
        self.area_page.add_child(instance=producto_sin_desc)
        response = self.client.get(producto_sin_desc.url)
        self.assertEqual(response.status_code, 200)

    def test_producto_page_carga_css_del_producto(self):
        response = self.client.get(self.producto_page.url)
        self.assertContains(response, "producto_page.css")

    def test_producto_page_titulo_tiene_clase_correcta(self):
        response = self.client.get(self.producto_page.url)
        self.assertContains(response, 'class="producto-titulo"')

    def test_producto_page_descripcion_tiene_clase_correcta(self):
        response = self.client.get(self.producto_page.url)
        self.assertContains(response, 'class="pagina-descripcion"')


# ============================================================
# 2. TESTS UNITARIOS — ProductoPage.get_context
# ============================================================

class TestProductoPageGetContext(WagtailPageTestCase):

    def setUp(self):
        _, self.homepage = crear_estructura_basica(self)
        self.area = AreaPage(title="Área test", titulo="Área test")
        self.homepage.add_child(instance=self.area)

        self.producto = ProductoPage(title="Producto test", titulo="Producto test")
        self.area.add_child(instance=self.producto)

        self.imagen = Image.objects.create(
            title="Test image", file=get_test_image_file()
        )

        self.e1 = ElementoPage(title="Primero", slug="primero", imagen=self.imagen)
        self.producto.add_child(instance=self.e1)

        self.e2 = ElementoPage(title="Segundo", slug="segundo", imagen=self.imagen)
        self.producto.add_child(instance=self.e2)

        self.e3 = ElementoPage(title="Tercero", slug="tercero", imagen=self.imagen)
        self.producto.add_child(instance=self.e3)

    def test_galeria_incluye_elementos_hijos(self):
        response = self.client.get(self.producto.url)
        self.assertContains(response, self.e1.url)

    def test_galeria_respeta_orden_del_arbol(self):
        response = self.client.get(self.producto.url)
        content = response.content.decode()
        pos1 = content.index(self.e1.url)
        pos2 = content.index(self.e2.url)
        pos3 = content.index(self.e3.url)
        self.assertLess(pos1, pos2)
        self.assertLess(pos2, pos3)

    def test_galeria_respeta_orden_modificado(self):
        self.e3.move(self.e1, pos="left")
        response = self.client.get(self.producto.url)
        content = response.content.decode()
        pos3 = content.index(self.e3.url)
        pos1 = content.index(self.e1.url)
        self.assertLess(pos3, pos1)


# ============================================================
# 3. TESTS UNITARIOS — ProductoPage.get_producto_anterior
# ============================================================

class ProductoPageNavegacionBase(WagtailPageTestCase):
    def setUp(self):
        _, self.homepage = crear_estructura_basica(self)
        self.area = AreaPage(title="Área test", titulo="Área test")
        self.homepage.add_child(instance=self.area)

        self.producto1 = ProductoPage(title="Producto 1", titulo="Producto uno")
        self.area.add_child(instance=self.producto1)

        self.producto2 = ProductoPage(title="Producto 2", titulo="Producto dos")
        self.area.add_child(instance=self.producto2)

        self.producto3 = ProductoPage(title="Producto 3", titulo="Producto tres")
        self.area.add_child(instance=self.producto3)

class TestProductoPageGetProductoAnterior(ProductoPageNavegacionBase):

    def test_devuelve_producto_anterior(self):
        self.assertEqual(self.producto2.get_producto_anterior(), self.producto1)

    def test_devuelve_none_si_no_hay_anterior(self):
        self.assertIsNone(self.producto1.get_producto_anterior())


# ============================================================
# 4. TESTS UNITARIOS — ProductoPage.get_producto_siguiente
# ============================================================

class TestProductoPageGetProductoSiguiente(ProductoPageNavegacionBase):
    """Verifica ProductoPage.get_producto_siguiente()."""

    def setUp(self):
        _, self.homepage = crear_estructura_basica(self)
        self.area = AreaPage(title="Área test", titulo="Área test")
        self.homepage.add_child(instance=self.area)

        self.producto1 = ProductoPage(title="Producto 1", titulo="Producto uno")
        self.area.add_child(instance=self.producto1)

        self.producto2 = ProductoPage(title="Producto 2", titulo="Producto dos")
        self.area.add_child(instance=self.producto2)

        self.producto3 = ProductoPage(title="Producto 3", titulo="Producto tres")
        self.area.add_child(instance=self.producto3)

    def test_devuelve_producto_siguiente(self):
        self.assertEqual(self.producto2.get_producto_siguiente(), self.producto3)

    def test_devuelve_none_si_no_hay_siguiente(self):
        self.assertIsNone(self.producto3.get_producto_siguiente())
