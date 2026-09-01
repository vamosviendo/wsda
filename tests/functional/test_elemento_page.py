import pytest

from django.utils.html import strip_tags
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


@pytest.fixture
def elemento_con_datos(elemento_factory, producto_page, objeto_imagen):
    data = {
        "title": "ElementoPage",
        "slug": "elemento_page",
        "imagen": objeto_imagen,
        "alt_imagen": "Imagen de elemento",
        "titulo": "Elemento con datos",
        "alto": 100,
        "ancho": 50,
        "unidad": "cm",
        "peso": 2,
        "unidad_peso": "kg",
        "descripcion": "<p>Descripción de elemento</p>",
        "comentarios": [
            ("comentario", "<p>Este es un comentario de prueba</p>"),
            ("comentario", "<p>Este es <em>otro</em> comentario de prueba</p>")
        ],
    }

    return elemento_factory(
        producto=producto_page,
        thumbnail=objeto_imagen,
        alt_thumbnail="Imagen de elemento con datos",
        titulo="Elemento con datos",
        page_data=data,
    )


def test_elemento_page(browser, producto_page, elemento_con_datos):
    # Dado un elemento incluido en una página de producto
    # si desde la página de producto cliqueamos en el elemento vamos a la
    # página del elemento.
    elemento = elemento_con_datos
    browser.get_page(producto_page.url)
    links_elemento = browser.wait_fors(".imagen a")
    links_elemento[0].click()
    assert "error" not in browser.title.lower()
    assert "not found" not in browser.title.lower()
    assert browser.current_url == browser.base_url + elemento.url

    # La página de elemento carga correctamente el css que le corresponde
    layout = browser.find_element(By.CSS_SELECTOR, "#elemento-layout")
    assert \
        browser.get_computed_style(layout, "display") == "flex", \
        "Los estilos css no se están aplicando correctamente"

    # La página de elemento muestra (en caso de que los haya) título,
    # descripción y comentarios
    titulo = browser.wait_for("#elemento-titulo")
    assert titulo.is_displayed()
    assert titulo.text == elemento.titulo

    descripcion=browser.wait_for("#elemento-descripcion")
    assert descripcion.is_displayed()
    assert descripcion.text == strip_tags(elemento.descripcion)

    comentarios = browser.wait_fors(".elemento-comentario")
    for index, comentario in enumerate(comentarios):
        assert comentario.is_displayed()
        assert comentario.text == strip_tags(elemento.comentarios[index].value.source)

    # En caso de que el título esté vacío, la página muestra "Sin título".
    elemento.titulo = ""
    elemento.save_revision().publish()
    browser.get_page(elemento.url)
    titulo = browser.wait_for("#elemento-titulo")
    assert titulo.is_displayed()
    assert titulo.text == "Sin título"

    # A la izquierda se muestra la imagen asociada al elemento
    img = browser.find_element(By.CSS_SELECTOR, "#elemento-img-preview")
    src = img.get_attribute("src")
    assert \
        browser.get_img_natural_width(img) > 0, \
        f"La imagen {src} no se cargó correctamente"


def test_visor_de_imagen_de_elemento(browser, elemento):
    browser.get_page(elemento.url)
    preview = browser.wait_for("#elemento-img-preview")
    # Si en la página de elemento pasamos el puntero sobre la imagen,
    # éste se muestra como zoom-in
    cursor = browser.get_computed_style(preview, "cursor")
    assert \
        cursor == "zoom-in", \
        f"El cursor de la imagen es {cursor} en lugar de zoom-in."

    # Si cliqueamos en la imagen
    # ésta se muestra a pantalla completa
    preview.click()
    overlay = browser.wait_for(".elemento-img-overlay.activo")
    assert overlay.is_displayed(), \
        "El overlay de imagen a pantalla completa no es visible " \
        "después de cliquear en la imagen."

    # En este estado (recién abierto) la imagen se ajusta al tamaño de la
    # pantalla.
    overlay_img = overlay.find_element(By.CSS_SELECTOR, "img")
    max_width = browser.get_computed_style(overlay_img, "maxWidth")
    max_height = browser.get_computed_style(overlay_img, "maxHeight")
    assert max_width != "none", \
        "Al abrirse el overlay de pantalla completa el ancho máximo " \
        "de la imagen debería estar definido (ajuste a ancho de pantalla)"
    assert max_height != "none", \
        "Al abrirse el overlay de pantalla completa la altura máxima " \
        "de la imagen debería estar definida (ajuste a alto de pantalla)"

    # Si cliqueamos en la imagen a pantalla completa, ésta se muestra
    # a tamaño real
    overlay.click()
    overlay_img = browser.wait_for(".elemento-img-overlay img")
    max_width = browser.get_computed_style(overlay_img, "maxWidth")
    assert max_width == "none",\
        "Tras cliquear en pantalla completa la imagen debería mostrarse " \
        "a tamaño real (maxWidth='none')"

    # Al cliquear en la imagen a tamaño real, volvemos a imagen ajustada
    # a pantalla
    overlay.click()
    overlay_img = browser.wait_for(".elemento-img-overlay img")
    max_width = browser.get_computed_style(overlay_img, "maxWidth")
    assert max_width != "none" \
        "Al volver desde imagen a tamaño real la imagen debería mostrarse " \
        "ajustada a pantalla."

    # Al cliquear en el botón X, deja de mostrarse la imagen a pantalla completa
    close_btn = browser.find_element(By.CSS_SELECTOR, ".elemento-img-close")
    close_btn.click()
    overlays_activos = browser.wait_fors(
        ".elemento-img-overlay.activo", fail=False
    )
    assert len(overlays_activos) == 0, \
        "El overlay de imagen a pantalla completa sigue mostrándose " \
        "después de pulsar el botón de cierre."

    # Al pulsar la tecla escape también se sale de pantalla completa
    preview = browser.wait_for("#elemento-img-preview")
    preview.click()
    browser.wait_for("body", By.TAG_NAME).send_keys(Keys.ESCAPE)
    overlays_activos = browser.wait_fors(
        ".elemento-img-overlay.activo", fail=False
    )
    assert len(overlays_activos) == 0, \
        "El overlay de imagen a pantalla completa sigue mostrándose " \
        "después de pulsar la tecla Escape."


def test_elemento_page_muestra_reproductor_de_video_local(
        browser, producto_page, elemento_factory, objeto_documento_video):
    """ Una ElementoPage de tipo video con contenido_multimedia local muestra
        un elemento <video controls> con la URL del documento.
    """
    elemento = elemento_factory(
        producto=producto_page,
        tipo="video",
        titulo="Video local",
        page_data={"contenido_multimedia": objeto_documento_video},
    )

    browser.get_page(elemento.url)

    video = browser.wait_for("#elemento-video video")
    assert video.is_displayed()

    src = video.get_attribute("src")
    assert src is not None
    assert "video_prueba.mp4" in src or "/documents/" in src


def test_elemento_page_muestra_reproductor_de_audio_local(
        browser, producto_page, elemento_factory, objeto_documento_audio):
    """ Una ElementoPage de tipo audio con contenido_multimedia local muestra
        un elemento <audio controls> con la URL del documento.
    """
    elemento = elemento_factory(
        producto=producto_page,
        tipo="audio",
        titulo="Audio local",
        page_data={"contenido_multimedia": objeto_documento_audio},
    )

    browser.get_page(elemento.url)

    audio = browser.wait_for("#elemento-audio audio")
    assert audio.is_displayed()

    src = audio.get_attribute("src")
    assert src is not None
    assert "audio_prueba.mp3" in src or "/documents/" in src


def test_contenido_multimedia_local_tiene_precedencia_sobre_url_externa(
        browser, producto_page, elemento_factory, objeto_documento_video):
    """ Si una ElementoPage tiene contenido_multimedia local y contenido_url
        externa (YouTube), se muestra el contenido local. NO se muestra el iframe.
    """
    elemento = elemento_factory(
        producto=producto_page,
        tipo="video",
        titulo="Video con local y url",
        page_data={
            "contenido_url": "https://www.youtube.com/watch?v=abc",
            "contenido_multimedia": objeto_documento_video,
        },
    )

    browser.get_page(elemento.url)

    video = browser.wait_for("#elemento-video video")
    assert video.is_displayed()

    iframes = browser.wait_fors("#elemento-video iframe", fail=False)
    assert len(iframes) == 0, \
        "Si hay contenido_multimedia local, no debe renderizarse el iframe de YouTube"
