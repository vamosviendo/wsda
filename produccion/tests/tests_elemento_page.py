from decimal import Decimal

from django.core.exceptions import ValidationError
from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from produccion.models import AreaPage, ElementoPage, ProductoPage


Image = get_image_model()


class ElementoPageTests(WagtailPageTestCase):

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
            title="Test image",
            file=get_test_image_file()
        )

        self.elemento = ElementoPage(title="Elemento test", imagen=self.imagen)
        self.producto.add_child(instance=self.elemento)

    def test_permite_guardar_y_recuperar_paginas_de_elemento(self):
        elemento = ElementoPage(
            title="Elemento recuperable",
            imagen=self.imagen,
            alt_imagen="Test image - texto alternativo",
            titulo="Test image",
            alto=2.5,
            ancho=1.0,
            profundidad=0.5,
            unidad="m",
            peso=2.0,
            descripcion="Descripción larga con muchos datos y palabras."
        )
        self.producto.add_child(instance=elemento)
        e = ElementoPage.objects.get(pk=elemento.pk)
        self.assertEqual([
            e.imagen,
            e.alt_imagen,
            e.titulo,
            e.alto,
            e.ancho,
            e.profundidad,
            e.unidad,
            e.peso,
            e.descripcion
        ], [
            self.imagen,
            "Test image - texto alternativo",
            "Test image",
            Decimal(2.5), Decimal(1.0), Decimal(0.5), "m",
            Decimal(2.0),
            "Descripción larga con muchos datos y palabras."
        ])

    def test_debe_tener_imagen(self):
        elemento = ElementoPage(
            title="Elemento sin imagen", slug="x", path="/", depth="0",
        )
        with self.assertRaises(ValidationError):
            elemento.full_clean()

    def test_elemento_is_renderable(self):
        self.assertPageIsRenderable(self.elemento)

    def test_titulo_fallback_cuando_vacio(self):
        sin_titulo = ElementoPage(
            imagen=self.imagen, title="x", slug="x", titulo=""
        )
        self.producto.add_child(instance=sin_titulo)
        response = self.client.get(sin_titulo.url)
        self.assertContains(response, "Sin título")

    def test_unidad_cm_por_defecto(self):
        self.assertEqual(self.elemento.unidad, "cm")

    def test_unidad_de_peso_kg_por_defecto(self):
        self.assertEqual(self.elemento.unidad_peso, "kg")

    def test_titulo_se_muestra_cuando_tiene_contenido(self):
        con_titulo = ElementoPage(
            imagen=self.imagen,
            title="y", slug="y", titulo="Retrato de mujer"
        )
        self.producto.add_child(instance=con_titulo)
        response = self.client.get(con_titulo.url)
        self.assertContains(response, "Retrato de mujer")
        self.assertNotContains(response, "Sin título")

    def test_solo_acepta_producto_page_como_padre(self):
        self.assertAllowedParentPageTypes(ElementoPage, {ProductoPage})

    def test_producto_page_muestra_hijos_en_galeria(self):
        response = self.client.get(self.producto.url)
        # el elemento creado en setUp debe aparecer en la página del producto
        print("URL:", self.elemento.url)
        self.assertContains(response, self.elemento.url)
