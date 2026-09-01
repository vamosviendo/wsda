from produccion.models import ElementoPage


def test_block_id_de_pagina_coincide_con_el_de_el_block(
        producto_page, elemento):
    block = producto_page.elementos[0]
    page = producto_page.get_children().specific().first()

    assert block.value.get("block_id") is not None
    assert page.block_id is not None
    assert block.value.get("block_id") == str(page.block_id)


def test_permite_guardar_imagenes(producto_page, objeto_imagen):
    elem = ElementoPage(
        title="Test", slug="test-img", thumbnail=objeto_imagen, tipo="imagen"
    )
    producto_page.add_child(instance=elem)
    assert elem.tipo == "imagen"
    assert elem.thumbnail == objeto_imagen


def test_permite_guardar_texto(producto_page):
    elem = ElementoPage(
        title="Test", slug="test-texto",
        tipo="texto", contenido_texto="<p>Texto de prueba</p>"
    )
    producto_page.add_child(instance=elem)
    assert elem.tipo == "texto"
    assert "<p>Texto de prueba</p>" in elem.contenido_texto


def test_permite_guardar_video_externo(producto_page):
    elem = ElementoPage(
        title="Test", slug="test-video", tipo="video",
        contenido_url="https://www.youtube.com/watch?v=abc"
    )
    producto_page.add_child(instance=elem)
    assert elem.tipo == "video"
    assert elem.contenido_url == "https://www.youtube.com/watch?v=abc"


def test_permite_guardar_audio_externo(producto_page):
    elem = ElementoPage(
        title="Test", slug="test-audio", tipo="audio",
        contenido_url="https://soundcloud.com/test"
    )
    producto_page.add_child(instance=elem)
    assert elem.tipo == "audio"
    assert elem.contenido_url == "https://soundcloud.com/test"


def test_permite_guardar_video_local(producto_page, objeto_documento_video):
    elem = ElementoPage(
        title="Test", slug="test-video-local", tipo="video",
        contenido_multimedia=objeto_documento_video
    )
    producto_page.add_child(instance=elem)
    elem.refresh_from_db()

    assert elem.tipo == "video"
    assert elem.contenido_multimedia == objeto_documento_video
    assert elem.contenido_multimedia.title == "documento de video de prueba"


def test_permite_guardar_audio_local(producto_page, objeto_documento_audio):
    elem = ElementoPage(
        title="Test", slug="test-audio-local", tipo="audio",
        contenido_multimedia=objeto_documento_audio
    )
    producto_page.add_child(instance=elem)
    elem.refresh_from_db()

    assert elem.tipo == "audio"
    assert elem.contenido_multimedia == objeto_documento_audio
    assert elem.contenido_multimedia.title == "documento de audio de prueba"

def test_contenido_multimedia_puede_ser_none(producto_page):
    elem = ElementoPage(
        title="Test", slug="test-video-local", tipo="video",
        contenido_multimedia=None
    )
    producto_page.add_child(instance=elem)
    elem.refresh_from_db()

    assert elem.contenido_multimedia is None


""" TODO: En la implementación actual, no se actualiza contenido_texto. 
    TODO: Es necesaria una propiedad ElementoPage.contenido que devuelva el contenido
          apropiado según el tipo. Si es tipo texto, devuelve contenido_texto. 
          Si es tipo video, devuelve contenido_url,
          Si es tipo imagen, devuelve thumbnail
    TODO: Establecer reglas en relación al tipo de contenido:
          - tipo texto: no permite contenido_url
          - tipo video: no permite contenido_texto
          - tipo imagen: no permite contenido_url ni contenido_texto
    TODO: Eliminar campos repetidos en ElementoPage y ElementoBlock. El único
          campo repetido debería ser block_id. Para todos los demás, ElementoBlock
          debería tomar su contenido de ElementoPage. O ElementoPage de ElementoBlock.
          Lo que sea más fácil.
    TODO: ¿Es posible crear y usar en wagtail una Page que incluya un Block como atributo,
          y ese block se use como campo StreamField de su página madre?
          Sería de la siguiente manera:
          Los valores que se ingresen en el Block de la Page se guardan como valores
          de los campos de la page. Page y block comparten campos y los valores
          de esos campos. Seguir pensando.
"""