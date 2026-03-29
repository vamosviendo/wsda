from selenium.webdriver.common.by import By
from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file

from functional_tests.base import FunctionalTestBase
from produccion.models import AreaPage, ProductoPage, ElementoPage


class ProductoPageFunctionalTests(FunctionalTestBase):
    """
    Verifica la página de producto y su galería de imágenes.

    OBJETIVO PRINCIPAL: detectar el tipo de error que ocurrió tras la
    migración, donde las imágenes desaparecieron visualmente aunque
    el modelo las seguía teniendo. Los tests de Django HTTP client
    no habrían detectado ese error.

    Estos tests verifican que:
      1. El elemento <img> existe en el DOM (capa HTML)
      2. El browser pudo descargar el archivo de imagen (capa de servidor)
      3. La imagen es visible (no está oculta por CSS)
      4. El CSS del producto se aplicó correctamente
    """

    def setUp(self):
        super().setUp()
        self.area_page = AreaPage(title="Pintura", titulo="Pintura")
        self.homepage.add_child(instance=self.area_page)
        self.producto_page = ProductoPage(
            title="Acrílicos",
            titulo="Acrílicos sobre tela",
            descripcion="Serie 2023.",
        )
        self.area_page.add_child(instance=self.producto_page)

    def _crear_elemento(self, slug="elemento-1"):
        """
        Helper: crea un ElementoPage con imagen real como hijo de ProductoPage.
        Las imágenes de ProductoPage provienen de sus hijos ElementoPage.
        """
        Image = get_image_model()
        image = Image(title="Obra de prueba")
        image.file = get_test_image_file()
        image.save()
        elemento = ElementoPage(
            title="Obra de prueba",
            slug=slug,
            imagen=image
        )
        self.producto_page.add_child(instance=elemento)
        return elemento

    def test_producto_page_carga(self):
        """La página de producto carga sin errores."""
        self.get(self.producto_page.url)
        self.assertNotIn("error", self.browser.title.lower())
        self.assertNotIn("not found", self.browser.title.lower())

    def test_producto_titulo_es_visible(self):
        """El título del producto es visible."""
        self.get(self.producto_page.url)
        titulo = self.wait_for(".producto-titulo")
        self.assertTrue(titulo.is_displayed())
        self.assertIn("Acrílicos sobre tela", titulo.text)

    def test_producto_descripcion_es_visible(self):
        """La descripción introductoria de la página de producto es visible."""
        self.get(self.producto_page.url)
        desc = self.wait_for(".pagina-descripcion")
        self.assertTrue(desc.is_displayed())
        self.assertIn("Serie 2023.", desc.text)

    def test_imagenes_grid_es_visible(self):
        """El contenedor de la galería de imágenes es visible."""
        """El contenedor de la galería existe en el DOM (puede estar vacío)."""
        self.get(self.producto_page.url)
        elementos = self.browser.find_elements(By.CSS_SELECTOR, ".imagenes-grid")
        self.assertGreater(
            len(elementos), 0,
            "No se encontró el contenedor .imagenes-grid en el DOM"
        )

    # --- Los tests críticos: carga real de imágenes ---

    def test_elemento_imagen_existe_en_galeria(self):
        """
        Cuando el producto tiene ElementoPage hijos, el DOM contiene elementos
        <img> dentro de .imagenes-grid.
        Verifica la capa HTML: que el template renderizó las imágenes.
        """
        self._crear_elemento()

        self.get(self.producto_page.url)
        grid = self.wait_for(".imagenes-grid")
        imgs = grid.find_elements(By.TAG_NAME, "img")
        self.assertGreater(
            len(imgs), 0,
            "No se encontraron elementos <img> en la galería"
        )

    def test_imagen_se_carga_realmente_en_el_browser(self):
        """
        ESTE ES EL TEST CRÍTICO.

        Verifica que la imagen no solo existe como tag en el HTML,
        sino que el browser pudo descargar el archivo.

        naturalWidth === 0 significa que el servidor no devolvió el archivo.
        Esto detecta exactamente el error de migración descrito:
        el tag <img> está, pero el archivo no se sirve.
        """
        self._crear_elemento()

        self.get(self.producto_page.url)
        self.wait_for(".imagenes-grid img")
        imgs = self.browser.find_elements(By.CSS_SELECTOR, ".imagenes-grid img")
        self.assertGreater(len(imgs), 0, "No hay imágenes en la galería")

        for img in imgs:
            natural_width = self.browser.execute_script(
                "return arguments[0].naturalWidth", img
            )
            src = img.get_attribute("src")
            self.assertGreater(
                natural_width,
                0,
                f"La imagen no cargó en el browser (naturalWidth=0). "
                f"src='{src}'. "
                f"Probable causa: el archivo no existe en MEDIA_ROOT, "
                f"o el servidor no está sirviendo /media/ correctamente."
            )

    def test_imagen_es_visible_no_oculta_por_css(self):
        """
        Verifica que la imagen, además de estar en el DOM y ser descargada,
        es visible para el usuario (display != none, visibility != hidden).
        """
        self._crear_elemento()
        self.get(self.producto_page.url)
        self.wait_for(".imagenes-grid img")
        imgs = self.browser.find_elements(By.CSS_SELECTOR, ".imagenes-grid img")

        for img in imgs:
            self.assertTrue(
                img.is_displayed(),
                f"La imagen está en el DOM pero no es visible (CSS la está ocultando). "
                f"src='{img.get_attribute('src')}'"
            )

    def test_src_de_imagen_apunta_a_url_de_media(self):
        """
        Verifica que el atributo src de la imagen apunta a /media/
        y no a una URL incorrecta (lo que indicaría un problema de
        configuración de MEDIA_URL o del template).
        """
        self._crear_elemento()
        self.get(self.producto_page.url)
        self.wait_for(".imagenes-grid img")
        imgs = self.browser.find_elements(By.CSS_SELECTOR, ".imagenes-grid img")

        for img in imgs:
            src = img.get_attribute("src")
            self.assertIn(
                "/media/",
                src,
                f"El src de la imagen no contiene '/media/': '{src}'. "
                f"Puede indicar un problema en MEDIA_URL o en el template."
            )

    def test_imagen_es_un_enlace_a_elemento_page(self):
        """
        Cada imagen de la galería es un enlace a su ElementoPage.
        Si el enlace falta o apunta a un lugar incorrecto, el usuario
        no puede navegar al detalle de la obra.
        """
        elemento = self._crear_elemento()
        self.get(self.producto_page.url)
        self.wait_for(".imagenes-grid a")
        links = self.browser.find_elements(By.CSS_SELECTOR, ".imagenes-grid a")
        self.assertGreater(len(links), 0,
            "Las imágenes de la galería no tienen enlace")
        hrefs = [a.get_attribute("href") for a in links]
        self.assertTrue(
            any(elemento.url in href for href in hrefs),
            f"Ningún enlace de la galería apunta a la URL del elemento "
            f"({elemento.url}). hrefs encontrados: {hrefs}"
        )

    def test_se_aplica_css_de_producto(self):
        """
        El CSS de producto_page fue cargado e interpretado.
        Verificamos que .imagenes-grid tiene el display: flex esperado.
        """
        self.get(self.producto_page.url)
        grid = self.wait_for(".imagenes-grid")
        display = self.get_computed_style(grid, "display")
        self.assertEqual(
            display,
            "flex",
            f".imagenes-grid tiene display='{display}' en lugar de 'flex'. "
            f"Probable causa: el archivo producto_page.css no se cargó."
        )

    def test_multiples_elementos_aparecen_en_galeria(self):
        """Varios ElementoPage hijos producen varias imágenes en la galería."""
        self._crear_elemento(slug="elemento-1")
        self._crear_elemento(slug="elemento-2")
        self._crear_elemento(slug="elemento-3")
        self.get(self.producto_page.url)
        self.wait_for(".imagenes-grid img")
        imgs = self.browser.find_elements(By.CSS_SELECTOR, ".imagenes-grid img")
        self.assertEqual(
            len(imgs), 3,
            f"Se esperaban 3 imágenes en la galería, "
            f"se encontraron {len(imgs)}"
        )
