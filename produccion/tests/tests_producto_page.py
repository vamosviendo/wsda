from django.test import RequestFactory
from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase
from wagtail.blocks import StreamValue

from produccion.models import AreaPage, ElementoPage, ProductoPage
from produccion.blocks import ElementoBlock, ElementosStreamBlock
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

        stream_data = [
            ("elemento", {"imagen": self.imagen, "alt_imagen": "Primero", "titulo": "Primero"}),
            ("elemento", {"imagen": self.imagen, "alt_imagen": "Segundo", "titulo": "Segundo"}),
            ("elemento", {"imagen": self.imagen, "alt_imagen": "Tercero", "titulo": "Tercero"}),
        ]
        self.producto.elementos = StreamValue(
            self.producto.elementos.stream_block,
            stream_data,
            is_lazy=False
        )
        self.producto.save()

    def test_galeria_incluye_elementos_hijos(self):
        e1 = self.producto.get_children().specific().first()
        response = self.client.get(self.producto.url)
        self.assertContains(response, e1.url)

    def test_galeria_respeta_orden_del_streamfield(self):
        response = self.client.get(self.producto.url)
        content = response.content.decode()
        pos1 = content.index("Primero")
        pos2 = content.index("Segundo")
        pos3 = content.index("Tercero")
        self.assertLess(pos1, pos2)
        self.assertLess(pos2, pos3)

    def test_galeria_respeta_orden_modificado(self):
        blocks = list(self.producto.elementos)
        block_ids = [str(b.value.get('block_id')) for b in blocks]

        stream_data_invertido = [
            ("elemento", {"imagen": self.imagen, "alt_imagen": "Tercero", "titulo": "Tercero", "block_id": block_ids[2]}),
            ("elemento", {"imagen": self.imagen, "alt_imagen": "Segundo", "titulo": "Segundo", "block_id": block_ids[1]}),
            ("elemento", {"imagen": self.imagen, "alt_imagen": "Primero", "titulo": "Primero", "block_id": block_ids[0]}),
        ]
        self.producto.elementos = StreamValue(
            self.producto.elementos.stream_block,
            stream_data_invertido,
            is_lazy=False
        )
        self.producto.save()

        response = self.client.get(self.producto.url)
        content = response.content.decode()
        pos3 = content.index("Tercero")
        pos1 = content.index("Primero")
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


# ============================================================
# 5. TESTS UNITARIOS — Sincronización StreamField y ElementoPage
# ============================================================

class TestProductoPageElementosStreamField(WagtailPageTestCase):
    """Tests de sincronización entre StreamField elementos y ElementoPage."""

    def setUp(self):
        _, self.homepage = crear_estructura_basica(self)
        self.area = AreaPage(title="Área test", titulo="Área test")
        self.homepage.add_child(instance=self.area)

        self.producto = ProductoPage(title="Producto test", titulo="Producto test")
        self.area.add_child(instance=self.producto)

        self.imagen1 = Image.objects.create(
            title="Imagen 1", file=get_test_image_file()
        )
        self.imagen2 = Image.objects.create(
            title="Imagen 2", file=get_test_image_file()
        )
        self.factory = RequestFactory()

    def test_al_guardar_producto_con_elementos_se_crean_paginas_hijas(self):
        """Al guardar un producto con elementos en el StreamField, se crean las ElementoPage."""
        stream_data = [
            ("elemento", {"imagen": self.imagen1, "alt_imagen": "Obra 1", "titulo": "Obra número uno"}),
            ("elemento", {"imagen": self.imagen2, "alt_imagen": "Obra 2", "titulo": "Obra número dos"}),
        ]

        self.producto.elementos = StreamValue(
            self.producto.elementos.stream_block,
            stream_data,
            is_lazy=False
        )
        self.producto.save()

        hijos = self.producto.get_children().specific()
        self.assertEqual(len(hijos), 2)

        titulos = [e.titulo for e in hijos]
        self.assertIn("Obra número uno", titulos)
        self.assertIn("Obra número dos", titulos)

    def test_al_modificar_titulo_en_block_se_actualiza_elemento_page(self):
        """Al modificar el título en el StreamField, se actualiza la ElementoPage."""
        stream_data = [
            ("elemento", {"imagen": self.imagen1, "alt_imagen": "Obra 1", "titulo": "Título original"}),
        ]

        self.producto.elementos = StreamValue(
            self.producto.elementos.stream_block,
            stream_data,
            is_lazy=False
        )
        self.producto.save()

        hijo = self.producto.get_children().specific().first()
        self.assertEqual(hijo.titulo, "Título original")

        stream_data_modificado = [
            ("elemento", {"imagen": self.imagen1, "alt_imagen": "Obra 1", "titulo": "Título modificado"}),
        ]

        self.producto.elementos = StreamValue(
            self.producto.elementos.stream_block,
            stream_data_modificado,
            is_lazy=False
        )
        self.producto.save()

        hijo.refresh_from_db()
        self.assertEqual(hijo.titulo, "Título modificado")

    def test_al_modificar_imagen_en_block_se_actualiza_elemento_page(self):
        """Al modificar la imagen en el StreamField, se actualiza la ElementoPage."""
        stream_data = [
            ("elemento", {"imagen": self.imagen1, "alt_imagen": "Obra 1", "titulo": "Obra test"}),
        ]

        self.producto.elementos = StreamValue(
            self.producto.elementos.stream_block,
            stream_data,
            is_lazy=False
        )
        self.producto.save()

        hijo = self.producto.get_children().specific().first()
        self.assertEqual(hijo.imagen, self.imagen1)

        imagen_nueva = Image.objects.create(
            title="Imagen nueva", file=get_test_image_file()
        )

        stream_data_modificado = [
            ("elemento", {"imagen": imagen_nueva, "alt_imagen": "Obra 1", "titulo": "Obra test"}),
        ]

        self.producto.elementos = StreamValue(
            self.producto.elementos.stream_block,
            stream_data_modificado,
            is_lazy=False
        )
        self.producto.save()

        hijo.refresh_from_db()
        self.assertEqual(hijo.imagen, imagen_nueva)

    def test_al_eliminar_block_se_elimina_elemento_page(self):
        """Al eliminar un block del StreamField, se elimina la ElementoPage."""
        stream_data = [
            ("elemento", {"imagen": self.imagen1, "alt_imagen": "Obra 1", "titulo": "Obra a eliminar"}),
            ("elemento", {"imagen": self.imagen2, "alt_imagen": "Obra 2", "titulo": "Obra a mantener"}),
        ]

        self.producto.elementos = StreamValue(
            self.producto.elementos.stream_block,
            stream_data,
            is_lazy=False
        )
        self.producto.save()

        self.assertEqual(self.producto.get_children().count(), 2)

        block_ids = [str(block.value.get('block_id')) for block in self.producto.elementos]

        stream_data_reducido = [
            ("elemento", {"imagen": self.imagen2, "alt_imagen": "Obra 2", "titulo": "Obra a mantener", "block_id": block_ids[1]}),
        ]

        self.producto.elementos = StreamValue(
            self.producto.elementos.stream_block,
            stream_data_reducido,
            is_lazy=False
        )
        self.producto.save()

        self.assertEqual(self.producto.get_children().count(), 1)
        hijo = self.producto.get_children().specific().first()
        self.assertEqual(hijo.titulo, "Obra a mantener")

    def test_al_reordenar_blocks_se_reordenan_paginas_hijas(self):
        """Al reordenar los blocks en el StreamField, el orden se refleja en get_context."""
        stream_data = [
            ("elemento", {"imagen": self.imagen1, "alt_imagen": "Obra 1", "titulo": "Primero"}),
            ("elemento", {"imagen": self.imagen2, "alt_imagen": "Obra 2", "titulo": "Segundo"}),
        ]

        self.producto.elementos = StreamValue(
            self.producto.elementos.stream_block,
            stream_data,
            is_lazy=False
        )
        self.producto.save()

        request = self.factory.get("/")
        context = self.producto.get_context(request)
        elementos_ordenados = [e.titulo for e in context["elementos"] if e]
        self.assertEqual(elementos_ordenados, ["Primero", "Segundo"])

        block_ids = [str(block.value.get('block_id')) for block in self.producto.elementos]

        stream_data_invertido = [
            ("elemento", {"imagen": self.imagen2, "alt_imagen": "Obra 2", "titulo": "Segundo", "block_id": block_ids[1]}),
            ("elemento", {"imagen": self.imagen1, "alt_imagen": "Obra 1", "titulo": "Primero", "block_id": block_ids[0]}),
        ]

        self.producto.elementos = StreamValue(
            self.producto.elementos.stream_block,
            stream_data_invertido,
            is_lazy=False
        )
        self.producto.save()

        request = self.factory.get("/")
        context = self.producto.get_context(request)
        elementos_ordenados = [e.titulo for e in context["elementos"] if e]
        self.assertEqual(elementos_ordenados, ["Segundo", "Primero"])


class TestElementoPageSincronizacion(WagtailPageTestCase):
    """Tests de sincronización desde ElementoPage hacia el StreamField del padre."""

    def setUp(self):
        _, self.homepage = crear_estructura_basica(self)
        self.area = AreaPage(title="Área test", titulo="Área test")
        self.homepage.add_child(instance=self.area)

        self.producto = ProductoPage(title="Producto test", titulo="Producto test")
        self.area.add_child(instance=self.producto)

        self.imagen1 = Image.objects.create(
            title="Imagen 1", file=get_test_image_file()
        )
        self.imagen2 = Image.objects.create(
            title="Imagen 2", file=get_test_image_file()
        )

    def test_al_modificar_titulo_en_elemento_page_se_actualiza_block(self):
        """Al modificar el título en ElementoPage, se actualiza el block en el padre."""
        stream_data = [
            ("elemento", {"imagen": self.imagen1, "alt_imagen": "Obra 1", "titulo": "Título original"}),
        ]

        self.producto.elementos = StreamValue(
            self.producto.elementos.stream_block,
            stream_data,
            is_lazy=False
        )
        self.producto.save()

        hijo = self.producto.get_children().specific().first()
        block_id = hijo.block_id

        hijo.titulo = "Título modificado desde elemento"
        hijo.save()

        self.producto.refresh_from_db()
        bloque = self.producto.elementos[0]
        self.assertEqual(bloque.value["titulo"], "Título modificado desde elemento")

    def test_al_modificar_imagen_en_elemento_page_se_actualiza_block(self):
        """Al modificar la imagen en ElementoPage, se actualiza el block en el padre."""
        stream_data = [
            ("elemento", {"imagen": self.imagen1, "alt_imagen": "Obra 1", "titulo": "Obra test"}),
        ]

        self.producto.elementos = StreamValue(
            self.producto.elementos.stream_block,
            stream_data,
            is_lazy=False
        )
        self.producto.save()

        hijo = self.producto.get_children().specific().first()

        imagen_nueva = Image.objects.create(
            title="Imagen nueva", file=get_test_image_file()
        )

        hijo.imagen = imagen_nueva
        hijo.save()

        self.producto.refresh_from_db()
        bloque = self.producto.elementos[0]
        self.assertEqual(bloque.value["imagen"], imagen_nueva)

    def test_no_se_crea_loop_al_actualizar_desde_elemento_page(self):
        """Al guardar ElementoPage, no se crea un loop infinito de actualizaciones."""
        stream_data = [
            ("elemento", {"imagen": self.imagen1, "alt_imagen": "Obra 1", "titulo": "Título"}),
        ]

        self.producto.elementos = StreamValue(
            self.producto.elementos.stream_block,
            stream_data,
            is_lazy=False
        )
        self.producto.save()

        hijo = self.producto.get_children().specific().first()

        hijo.titulo = "Título actualizado"
        hijo.save()

        self.producto.refresh_from_db()
        bloque = self.producto.elementos[0]

        self.assertEqual(bloque.value["titulo"], "Título actualizado")

    def test_elemento_page_sin_block_id_no_actualiza_padre(self):
        """Una ElementoPage creada directamente (sin block_id) no rompe el sistema."""
        imagen = Image.objects.create(
            title="Imagen", file=get_test_image_file()
        )
        elemento = ElementoPage(
            title="Elemento legacy",
            slug="elemento-legacy",
            imagen=imagen,
            titulo="Título legacy"
        )
        self.producto.add_child(instance=elemento)

        elemento.titulo = "Nuevo título"
        elemento.save()

        self.producto.refresh_from_db()
        self.assertEqual(len(self.producto.elementos), 0)

    def test_elemento_page_con_block_id_sincroniza_al_guardar(self):
        """Una ElementoPage con block_id sincroniza automáticamente al guardar."""
        stream_data = [
            ("elemento", {"imagen": self.imagen1, "alt_imagen": "Obra 1", "titulo": "Título inicial"}),
        ]

        self.producto.elementos = StreamValue(
            self.producto.elementos.stream_block,
            stream_data,
            is_lazy=False
        )
        self.producto.save()

        hijo = self.producto.get_children().specific().first()
        self.assertIsNotNone(hijo.block_id)

        hijo.titulo = "Sincronizado"
        hijo.save()

        self.producto.refresh_from_db()
        self.assertEqual(self.producto.elementos[0].value["titulo"], "Sincronizado")


class TestProductoPageElementosStreamFieldEdgeCases(WagtailPageTestCase):
    """Tests de casos borde."""

    def setUp(self):
        _, self.homepage = crear_estructura_basica(self)
        self.area = AreaPage(title="Área test", titulo="Área test")
        self.homepage.add_child(instance=self.area)

        self.producto = ProductoPage(title="Producto test", titulo="Producto test")
        self.area.add_child(instance=self.producto)

        self.imagen = Image.objects.create(
            title="Imagen test", file=get_test_image_file()
        )

    def test_producto_sin_elementos_no_tiene_hijos(self):
        """Un producto sin elementos en StreamField no tiene hijos ElementoPage."""
        self.producto.elementos = StreamValue(
            stream_block=ElementoBlock(),
            stream_data=[],
            is_lazy=False
        )
        self.producto.save()

        self.assertEqual(self.producto.get_children().count(), 0)

    def test_elementos_sin_imagen_en_block(self):
        """Un block sin imagen se sincroniza correctamente (imagen=None en ElementoPage)."""
        stream_data = [
            ("elemento", {"imagen": None, "alt_imagen": "Sin imagen", "titulo": "Sin imagen"})
        ]

        self.producto.elementos = StreamValue(
            self.producto.elementos.stream_block,
            stream_data,
            is_lazy=False
        )
        self.producto.save()

        hijos = self.producto.get_children().specific()
        self.assertEqual(len(hijos), 1)
        self.assertIsNone(hijos[0].imagen)

    def test_eliminar_producto_no_rompe(self):
        """Al eliminar un producto, no falla la sincronización."""
        stream_data = [
            ("elemento", {"imagen": self.imagen, "alt_imagen": "Obra", "titulo": "Obra"})
        ]

        self.producto.elementos = StreamValue(
            self.producto.elementos.stream_block,
            stream_data,
            is_lazy=False
        )
        self.producto.save()

        self.producto.delete()


class TestElementosSinBlockIdNoSeMuestran(WagtailPageTestCase):
    """Tests para verificar que elementos sin block_id no se muestran."""

    def setUp(self):
        _, self.homepage = crear_estructura_basica(self)
        self.area = AreaPage(title="Área test", titulo="Área test")
        self.homepage.add_child(instance=self.area)

        self.producto = ProductoPage(title="Producto test", titulo="Producto test")
        self.area.add_child(instance=self.producto)

        self.imagen = Image.objects.create(
            title="Imagen test", file=get_test_image_file()
        )
        self.factory = RequestFactory()

    def test_elementos_sin_block_id_no_se_muestran(self):
        """Los elementos creados directamente (sin block_id) no deben mostrarse."""
        stream_data = [
            ("elemento", {"imagen": self.imagen, "alt_imagen": "Con block", "titulo": "Elemento con block"}),
        ]
        self.producto.elementos = StreamValue(
            self.producto.elementos.stream_block,
            stream_data,
            is_lazy=False
        )
        self.producto.save()

        elemento_legacy = ElementoPage(
            title="Legacy sin block",
            slug="legacy-sin-block",
            imagen=self.imagen,
            titulo="Legacy sin block"
        )
        self.producto.add_child(instance=elemento_legacy)

        self.assertIsNone(elemento_legacy.block_id)

        request = self.factory.get("/")
        context = self.producto.get_context(request)

        titulos_en_contexto = [
            e.titulo for e in context["elementos"] if e
        ]

        self.assertIn("Elemento con block", titulos_en_contexto)
        self.assertNotIn("Legacy sin block", titulos_en_contexto)

    def test_block_id_no_aparece_en_formulario_element_block(self):
        """El campo block_id no debe aparecer visible en el formulario del ElementoBlock."""
        from produccion.blocks import ElementoBlock
        block = ElementoBlock()
        block_id_block = block.child_blocks['block_id']
        self.assertEqual(
            block_id_block.meta.group,
            'hidden-input',
            "block_id debe tener group='hidden-input' para ocultarse del formulario"
        )
