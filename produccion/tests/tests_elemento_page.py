from django.core.exceptions import ValidationError
from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from produccion.models import AreaPage, ElementoPage, ProductoPage


Image = get_image_model()


class ElementoPageBase(WagtailPageTestCase):
    def setUp(self):
        root_page = Page.get_first_root_node()
        Site.objects.update_or_create(
            hostname="testsite",
            defaults={
                "root_page": root_page,
                "is_default_site": True,
            },
        )
        area = AreaPage(title="Área test", titulo="Área test")
        root_page.add_child(instance=area)

        self.producto = ProductoPage(title="Producto test", titulo="Producto test")
        area.add_child(instance=self.producto)

        self.imagen = Image.objects.create(
            title="Test image", file=get_test_image_file()
        )


# ============================================================
# 1. TESTS FUNCIONALES — ElementoPage
# ============================================================

class ElementoPageFunctionalTests(ElementoPageBase):

    def test_titulo_fallback_cuando_vacio(self):
        sin_titulo = ElementoPage(
            imagen=self.imagen, title="x", slug="x", titulo=""
        )
        self.producto.add_child(instance=sin_titulo)
        response = self.client.get(sin_titulo.url)
        self.assertContains(response, "Sin título")

    def test_titulo_se_muestra_cuando_tiene_contenido(self):
        con_titulo = ElementoPage(
            imagen=self.imagen,
            title="y", slug="y", titulo="Retrato de mujer"
        )
        self.producto.add_child(instance=con_titulo)
        response = self.client.get(con_titulo.url)
        self.assertContains(response, "Retrato de mujer")
        self.assertNotContains(response, "Sin título")


# ============================================================
# 2. TESTS UNITARIOS — ElementoPage defaults
# ============================================================

class TestElementoPageDefaults(ElementoPageBase):
    def setUp(self):
        super().setUp()
        self.elemento = ElementoPage(imagen=self.imagen, title="x", slug="x")
        self.producto.add_child(instance=self.elemento)

    def test_unidad_cm_por_defecto(self):
        self.assertEqual(self.elemento.unidad, "cm")

    def test_unidad_de_peso_kg_por_defecto(self):
        self.assertEqual(self.elemento.unidad_peso, "kg")


# ============================================================
# 3. TESTS UNITARIOS — ElementoPage.full_clean
# ============================================================

class TestElementoPageFullClean(ElementoPageBase):

    def test_debe_tener_imagen(self):
        elemento = ElementoPage(title="Sin imagen", slug="x")
        with self.assertRaises(ValidationError):
            elemento.full_clean()
