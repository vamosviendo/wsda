from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file

from functional_tests.base import FunctionalTestBase
from produccion.models import AreaPage, ProductoPage, ElementoPage


class ElementoPageFunctionalTests(FunctionalTestBase):
    """
    Verifica la página de elemento individual: contenido y visor de imagen JS.

    El visor tiene tres estados:
      0 — cerrado (overlay oculto)
      1 — pantalla completa (imagen ajustada a la pantalla)
      2 — tamaño real (imagen a resolución nativa, con scroll si es necesario)

    Transiciones:
      clic en preview  → estado 1
      clic en overlay  → estado 1 → 2 → 1 → 2 ...
      clic en botón X  → estado 0
      tecla Escape     → estado 0
    """

    def setUp(self):
        super().setUp()
        area_page = AreaPage(title="Pintura", titulo="Pintura")
        self.homepage.add_child(instance=area_page)
        self.producto_page = ProductoPage(title="Acrílicos", titulo="Acrílicos")
        area_page.add_child(instance=self.producto_page)

        Image = get_image_model()
        self.image = Image(title="Obra test")
        self.image.file = get_test_image_file()
        self.image.save()

        self.elemento = ElementoPage(
            title="Retrato de mujer",
            slug="retrato-de-mujer",
            imagen=self.image,
            alt_imagen="Retrato de mujer, acrílico sobre tela",
            titulo="Retrato de mujer",
            alto=80,
            ancho=60,
            unidad="cm",
            descripcion="<p>Descripción de la obra.</p>",
        )
        self.producto_page.add_child(instance=self.elemento)

    # --- Contenido ---

    def test_elemento_page_carga(self):
        """La página del elemento carga sin errores."""
        self.get(self.elemento.url)
        self.assertNotIn("error", self.browser.title.lower())
        self.assertNotIn("not found", self.browser.title.lower())

    def test_elemento_titulo_es_visible(self):
        """El título de la obra es visible."""
        self.get(self.elemento.url)
        titulo = self.wait_for(".elemento-titulo")
        self.assertTrue(titulo.is_displayed())
        self.assertIn("retrato de mujer", titulo.text.lower())

    def test_elemento_dimensiones_son_visibles(self):
        """Las dimensiones (alto × ancho, unidad) son visibles."""
        self.get(self.elemento.url)
        dims = self.wait_for(".elemento-dimensiones")
        self.assertTrue(dims.is_displayed())
        text = dims.text
        self.assertIn("80", text)
        self.assertIn("60", text)
        self.assertIn("cm", text)

    def test_elemento_descripcion_es_visible(self):
        """La descripción de la obra es visible."""
        self.get(self.elemento.url)
        desc = self.wait_for(".elemento-descripcion")
        self.assertTrue(desc.is_displayed())
        self.assertIn("Descripción de la obra.", desc.text)

    def test_elemento_imagen_carga_en_el_browser(self):
        """
        La imagen de la obra fue descargada correctamente por el browser.
        naturalWidth === 0 significa que el archivo no se sirvió.
        """
        self.get(self.elemento.url)
        img = self.wait_for(".elemento-img-preview")
        natural_width = self.browser.execute_script(
            "return arguments[0].naturalWidth", img
        )
        src = img.get_attribute("src")
        self.assertGreater(
            natural_width, 0,
            f"La imagen de la obra no cargó (naturalWidth=0). src='{src}'"
        )

    def test_elemento_imagen_src_apunta_a_media(self):
        """El src de la imagen apunta a /media/."""
        self.get(self.elemento.url)
        img = self.wait_for(".elemento-img-preview")
        src = img.get_attribute("src")
        self.assertIn(
            "/media/", src,
            f"El src no contiene '/media/': '{src}'"
        )

    def test_elemento_css_se_aplica(self):
        """
        El CSS del elemento fue cargado. Verificamos el layout de dos columnas:
        .elemento-layout debe tener display: flex.
        """
        self.get(self.elemento.url)
        layout = self.wait_for(".elemento-layout")
        display = self.get_computed_style(layout, "display")
        self.assertEqual(
            display, "flex",
            f".elemento-layout tiene display='{display}' "
            f"en lugar de 'flex'"
        )

    # --- Visor de imagen JS ---

    def _abrir_overlay(self):
        """Helper: carga la página y cliquea la imagen preview para abrir el overlay."""
        self.get(self.elemento.url)
        preview = self.wait_for(".elemento-img-preview")
        preview.click()
        WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".elemento-img-overlay.activo")
            )
        )

    def test_imagen_preview_tiene_cursor_zoom_in(self):
        """
        El cursor sobre la imagen preview es zoom-in, indicando al usuario
        que puede ampliarla.
        """
        self.get(self.elemento.url)
        preview = self.wait_for(".elemento-img-preview")
        cursor = self.get_computed_style(preview, "cursor")
        self.assertEqual(
            cursor, "zoom-in",
            f"El cursor de la imagen preview es '{cursor}' "
            f"en lugar de 'zoom-in'"
        )

    def test_clic_en_preview_abre_overlay(self):
        """Al cliquear la imagen preview, el overlay aparece."""
        self._abrir_overlay()
        overlay = self.browser.find_element(
            By.CSS_SELECTOR, ".elemento-img-overlay.activo"
        )
        self.assertTrue(
            overlay.is_displayed(),
            "El overlay no es visible después de cliquear la imagen"
        )

    def test_overlay_estado_1_imagen_ajustada_a_pantalla(self):
        """
        En estado 1 (recién abierto), la imagen del overlay tiene
        max-width y max-height definidos, lo que la ajusta a la pantalla.
        """
        self._abrir_overlay()
        overlay_img = self.browser.find_element(
            By.CSS_SELECTOR, ".elemento-img-overlay img"
        )
        max_width = self.get_computed_style(overlay_img, "maxWidth")
        max_height = self.get_computed_style(overlay_img, "maxHeight")
        self.assertNotEqual(
            max_width, "none",
            "En estado 1, maxWidth debería estar definido "
            "(ajuste a pantalla)"
        )
        self.assertNotEqual(
            max_height, "none",
            "En estado 1, maxHeight debería estar definido "
            "(ajuste a pantalla)"
        )

    def test_clic_en_overlay_pasa_a_estado_2_tamanio_real(self):
        """
        Al cliquear el overlay en estado 1, se pasa al estado 2:
        la imagen se muestra a tamaño real (max-width: none).
        """
        self._abrir_overlay()
        overlay = self.browser.find_element(
            By.CSS_SELECTOR, ".elemento-img-overlay.activo"
        )
        overlay.click()
        # Dar tiempo al JS para actualizar el estilo
        import time;
        time.sleep(0.3)
        overlay_img = self.browser.find_element(
            By.CSS_SELECTOR, ".elemento-img-overlay img"
        )
        max_width = self.get_computed_style(overlay_img, "maxWidth")
        self.assertEqual(
            max_width, "none",
            f"En estado 2, maxWidth debería ser 'none' (tamaño real). "
            f"Valor actual: '{max_width}'"
        )

    def test_clic_en_overlay_estado_2_vuelve_a_estado_1(self):
        """
        Al cliquear el overlay en estado 2, se vuelve al estado 1:
        la imagen vuelve a estar ajustada a la pantalla (max-width definido).
        """
        self._abrir_overlay()
        overlay = self.browser.find_element(
            By.CSS_SELECTOR, ".elemento-img-overlay.activo"
        )
        overlay.click()  # → estado 2
        import time;
        time.sleep(0.3)
        overlay.click()  # → estado 1
        time.sleep(0.3)
        overlay_img = self.browser.find_element(
            By.CSS_SELECTOR, ".elemento-img-overlay img"
        )
        max_width = self.get_computed_style(overlay_img, "maxWidth")
        self.assertNotEqual(
            max_width, "none",
            f"Al volver al estado 1, maxWidth debería estar definido. "
            f"Valor actual: '{max_width}'"
        )

    def test_boton_cerrar_cierra_overlay(self):
        """Al cliquear el botón X, el overlay desaparece."""
        self._abrir_overlay()
        close_btn = self.browser.find_element(
            By.CSS_SELECTOR, ".elemento-img-close"
        )
        close_btn.click()
        import time;
        time.sleep(0.3)
        overlays_activos = self.browser.find_elements(
            By.CSS_SELECTOR, ".elemento-img-overlay.activo"
        )
        self.assertEqual(
            len(overlays_activos), 0,
            "El overlay sigue visible después de cliquear el botón de cierre"
        )

    def test_escape_cierra_overlay(self):
        """Al presionar Escape, el overlay desaparece."""
        self._abrir_overlay()
        self.browser.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        import time;
        time.sleep(0.3)
        overlays_activos = self.browser.find_elements(
            By.CSS_SELECTOR, ".elemento-img-overlay.activo"
        )
        self.assertEqual(
            len(overlays_activos), 0,
            "El overlay sigue visible después de presionar Escape"
        )
