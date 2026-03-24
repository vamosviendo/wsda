from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file
from wagtail.test.utils import WagtailPageTestCase

from produccion.models import AreaPage, ElementoPage, ProductoPage
from utils.test_utils import crear_estructura_basica


Image = get_image_model()


# ============================================================
# 5. TESTS UNITARIOS — Jerarquía de páginas
# ============================================================

class PageHierarchyTests(WagtailPageTestCase):
    """
    Verifica que la jerarquía de páginas funciona como se espera:
    HomePage → AreaPage → ProductoPage
    """

    def setUp(self):
        _, self.homepage = crear_estructura_basica(self)
        self.area_page = AreaPage(title="Pintura", titulo="Pintura")
        self.homepage.add_child(instance=self.area_page)
        self.producto_page = ProductoPage(title="Test", titulo="Test")
        self.area_page.add_child(instance=self.producto_page)

    def test_area_page_is_child_of_homepage(self):
        """AreaPage puede ser hija de HomePage."""
        self.assertIn(
            self.area_page,
            [p.specific for p in self.homepage.get_children()]
        )

    def test_producto_page_is_child_of_area_page(self):
        """ProductoPage puede ser hija de AreaPage."""
        producto = ProductoPage(title="Test", titulo="Test")
        self.area_page.add_child(instance=producto)
        self.assertIn(
            producto,
            [p.specific for p in self.area_page.get_children()]
        )

    def test_elemento_page_is_child_of_producto_page(self):
        """ElementoPage puede ser hija de ProductoPage-"""
        imagen = Image.objects.create(
            title="Test image",
            file=get_test_image_file()
        )
        elemento = ElementoPage(title="Elemento test", imagen=imagen)
        self.producto_page.add_child(instance=elemento)
        self.assertIn(
            elemento,
            [p.specific for p in self.producto_page.get_children()]
        )

    def test_multiple_area_pages_under_homepage(self):
        """Pueden coexistir múltiples AreaPages bajo una misma HomePage."""
        area2 = AreaPage(title="Grabado", titulo="Grabado")
        self.homepage.add_child(instance=area2)
        area_count = AreaPage.objects.filter(
            pk__in=self.homepage.get_children().values_list("pk", flat=True)
        ).count()
        self.assertEqual(area_count, 2)
