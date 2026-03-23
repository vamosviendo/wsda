from decimal import Decimal

from django.core.exceptions import ValidationError
from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from home.models import HomePage
from produccion.models import AreaPage, ElementoPage, ProductoPage


Image = get_image_model()


# ============================================================
# Fixture compartida entre test classes
# ============================================================

def crear_estructura_basica(test_case):
    """
    Crea la estructura mínima necesaria:
      root → site (testsite)
           → homepage
    Devuelve (root_page, homepage).
    Llama a esto en setUp() de cada clase.
    """
    root_page = Page.get_first_root_node()
    homepage = HomePage(title="Home")
    root_page.add_child(instance=homepage)
    Site.objects.create(
        hostname="testsite",
        root_page=homepage,
        is_default_site=True,
        site_name="Liliana Medela",
    )
    return root_page, homepage


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
# 2. TESTS FUNCIONALES — ProductoPage
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
# 3. TESTS UNITARIOS — AreaPage
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


# ============================================================
# 4. TESTS UNITARIOS — ProductoPage
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

    def test_multiple_area_pages_under_homepage(self):
        """Pueden coexistir múltiples AreaPages bajo una misma HomePage."""
        area2 = AreaPage(title="Grabado", titulo="Grabado")
        self.homepage.add_child(instance=area2)
        area_count = AreaPage.objects.filter(
            pk__in=self.homepage.get_children().values_list("pk", flat=True)
        ).count()
        self.assertEqual(area_count, 2)

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
