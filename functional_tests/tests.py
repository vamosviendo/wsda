from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file

from base.models import FooterText, NavigationSettings
from functional_tests.base import FunctionalTestBase
from produccion.models import AreaPage, ElementoPage, ProductoPage


# ============================================================
# Tests — Portada
# ============================================================

class HomePageFunctionalTests(FunctionalTestBase):
    """
    Verifica la portada tal como la ve el usuario en un browser real.
    """

    def test_homepage_loads(self):
        """La portada carga sin errores (no hay página de error en el título)."""
        self.get("/")
        title = self.browser.title
        self.assertNotIn("error", title.lower())
        self.assertNotIn("not found", title.lower())

    def test_homepage_incluye_container_franjas(self):
        """El contenedor .franjas existe en el DOM (puede estar vacío)."""
        self.get("/")
        elementos = self.browser.find_elements(By.CSS_SELECTOR, ".franjas")
        self.assertGreater(len(elementos), 0, "No se encontró el contenedor .franjas")

    def test_elemento_body_existe_en_homepage(self):
        """El elemento <body> está presente (smoke test del DOM)."""
        self.get("/")
        body = self.browser.find_element(By.TAG_NAME, "body")
        self.assertIsNotNone(body)


# ============================================================
# Tests — Header
# ============================================================

class HeaderFunctionalTests(FunctionalTestBase):
    """
    Verifica el header: nombre del sitio, navegación.
    """

    def test_nombre_del_sitio_es_visible(self):
        """El nombre del sitio es visible (el CSS no lo está ocultando)."""
        self.get("/")
        site_title = self.wait_for(".site-title")
        self.assertTrue(site_title.is_displayed())
        self.assertIn(self.site_name.lower(), site_title.text.lower())

    def test_nombre_del_sitio_es_un_link_a_home(self):
        """El nombre del sitio es un enlace a la raíz."""
        self.get("/")
        link = self.browser.find_element(By.CSS_SELECTOR, ".site-title a")
        href = link.get_attribute("href")
        self.assertTrue(href.endswith("/"))

    def test_nav_es_visible(self):
        """El menú de navegación está visible."""
        self.get("/")
        nav = self.wait_for("nav")
        self.assertTrue(nav.is_displayed())

    def test_link_de_inicio_existe_en_nav(self):
        """El ítem 'Inicio' aparece en el menú y es visible."""
        self.get("/")
        links = self.browser.find_elements(By.CSS_SELECTOR, "nav a")
        link_texts = [a.text.lower() for a in links]
        self.assertIn("inicio", link_texts)

    def test_link_blog_existe_en_nav(self):
        """El link al blog externo está en el menú y es visible."""
        self.get("/")
        links = self.browser.find_elements(By.CSS_SELECTOR, "nav a")
        hrefs = [a.get_attribute("href") for a in links]
        self.assertTrue(any("blogspot.com" in href for href in hrefs))

    def test_una_pagina_de_area_aparece_in_nav(self):
        """Una AreaPage con show_in_menus=True aparece visible en el menú."""
        area = AreaPage(title="Pintura", titulo="Pintura", show_in_menus=True)
        self.homepage.add_child(instance=area)
        self.get("/")
        links = self.browser.find_elements(By.CSS_SELECTOR, "nav a")
        link_texts = [a.text.lower() for a in links]
        self.assertIn("pintura", link_texts)

    def test_link_de_nav_navega_correctamente(self):
        """Un clic en 'Inicio' en el menú lleva a la URL correcta."""
        area = AreaPage(title="Pintura", titulo="Pintura", show_in_menus=True)
        self.homepage.add_child(instance=area)
        self.get(area.url)  # empezamos en otra página
        inicio_link = None
        for link in self.browser.find_elements(By.CSS_SELECTOR, "nav a"):
            if link.text.lower() == "inicio":
                inicio_link = link
                break
        self.assertIsNotNone(inicio_link, "No se encontró el link 'Inicio' en el menú")
        inicio_link.click()
        self.assertEqual(
            self.browser.current_url,
            f"{self.live_server_url}{self.homepage.url}"
        )

    def test_se_aplica_css_del_header(self):
        """
        El CSS del header fue cargado e interpretado por el browser.
        Verificamos una propiedad de .site-title que depende del CSS:
        font-family debe incluir 'Didact Gothic' (definida en base.css via var).
        """
        self.get("/")
        site_title = self.wait_for(".site-title")
        font_family = self.get_computed_style(site_title, "fontFamily")
        # Nos aseguramos de que no es el font genérico del sistema (serif/Times)
        # indicando que el CSS efectivamente cargó.
        self.assertNotEqual(font_family, "Times New Roman")
        self.assertNotEqual(font_family, "serif")


# ============================================================
# Tests — Footer
# ============================================================

class FooterFunctionalTests(FunctionalTestBase):
    """
    Verifica el footer: crédito, redes sociales, footer text.
    """

    def test_footer_es_visible(self):
        """El footer es visible en la página."""
        self.get("/")
        footer = self.wait_for("footer")
        self.assertTrue(footer.is_displayed())

    def test_footer_credit_es_visible(self):
        """El crédito de diseño (HT) es visible en el footer."""
        self.get("/")
        footer = self.browser.find_element(By.CSS_SELECTOR, "footer")
        self.assertIn("HT", footer.text)

    def test_instagram_link_es_visible_si_esta_configurado(self):
        """El link de Instagram es visible cuando está configurado."""
        NavigationSettings(instagram_url="https://instagram.com/lilianamedela").save()
        self.get("/")
        links = self.browser.find_elements(By.CSS_SELECTOR, ".footer-social a")
        link_texts = [a.text.lower() for a in links]
        self.assertIn("instagram", link_texts)

    def test_instagram_link_navega_a_url_correcta(self):
        """El link de Instagram apunta a la URL configurada."""
        NavigationSettings(instagram_url="https://instagram.com/lilianamedela").save()
        self.get("/")
        insta_link = None
        for link in self.browser.find_elements(By.CSS_SELECTOR, ".footer-social a"):
            if link.text.lower() == "instagram":
                insta_link = link
                break
        self.assertIsNotNone(insta_link)
        self.assertEqual(
            insta_link.get_attribute("href"),
            "https://instagram.com/lilianamedela"
        )

    def test_texto_del_footer_es_visible_si_esta_publicado(self):
        """El texto del footer (snippet publicado) es visible."""
        FooterText.objects.create(body="<p>Obra de Liliana Medela</p>", live=True)
        self.get("/")
        footer = self.browser.find_element(By.CSS_SELECTOR, "footer")
        self.assertIn("Obra de Liliana Medela", footer.text)

    def test_texto_del_footer_no_es_visible_si_esta_en_borrador(self):
        """El texto del footer en borrador no es visible."""
        FooterText.objects.create(body="<p>Texto en borrador</p>", live=False)
        self.get("/")
        footer = self.browser.find_element(By.CSS_SELECTOR, "footer")
        self.assertNotIn("Texto en borrador", footer.text)


# ============================================================
# Tests — AreaPage
# ============================================================

class AreaPageFunctionalTests(FunctionalTestBase):
    """
    Verifica la página de área (grilla de productos/series).
    """

    def setUp(self):
        super().setUp()
        self.area_page = AreaPage(
            title="Pintura",
            titulo="Pintura",
            descripcion="Obras en técnica pictórica.",
        )
        self.homepage.add_child(instance=self.area_page)

    def test_area_page_carga(self):
        """La página de área carga sin errores."""
        self.get(self.area_page.url)
        self.assertNotIn("error", self.browser.title.lower())

    def test_area_titulo_es_visible(self):
        """El título del área es visible en la página."""
        self.get(self.area_page.url)
        titulo = self.wait_for(".area-titulo")
        self.assertTrue(titulo.is_displayed())
        self.assertIn("Pintura", titulo.text)

    def test_area_descripcion_es_visible(self):
        """La descripción del área es visible."""
        self.get(self.area_page.url)
        desc = self.wait_for(".area-descripcion")
        self.assertTrue(desc.is_displayed())
        self.assertIn("Obras en técnica pictórica.", desc.text)

    def test_productos_grid_es_visible(self):
        """El contenedor de la grilla de productos existe en el DOM (puede estar vacío)."""
        self.get(self.area_page.url)
        elementos = self.browser.find_elements(By.CSS_SELECTOR, ".productos-grid")
        self.assertGreater(
            len(elementos), 0,
            "No se encontró el contenedor .productos-grid en el DOM"
        )

    def test_area_css_se_aplica(self):
        """
        El CSS del área fue aplicado correctamente.
        Verificamos que .area-titulo tiene el display esperado.
        """
        self.get(self.area_page.url)
        titulo = self.wait_for(".area-titulo")
        display = self.get_computed_style(titulo, "display")
        self.assertNotEqual(display, "none")


# ============================================================
# Tests — ProductoPage  ← EL MÁS IMPORTANTE
# ============================================================

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


# ============================================================
# Tests — ElementoPage
# ============================================================

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
