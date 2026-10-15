from pytest_django import asserts

from produccion.models import ElementoPage


def test_usa_template_correcto(elemento, client):
    response = client.get(elemento.url)
    asserts.assertTemplateUsed(response, "produccion/elemento_page.html")


def test_block_id_de_pagina_coincide_con_el_de_el_block(
        elemento_compuesto, elemento):
    block = elemento_compuesto.elementos[0]
    page = elemento_compuesto.get_children().specific().first()

    assert block.value.get("block_id") is not None
    assert page.block_id is not None
    assert block.value.get("block_id") == str(page.block_id)


def test_titulo_vacio_se_guarda_como_cadena_vacia(elemento_compuesto):
    elem = ElementoPage(
        title="Test", slug="test-sin-titulo", titulo=""
    )
    elemento_compuesto.add_child(instance=elem)
    assert elem.titulo == ""


def test_permite_guardar_imagenes(elemento_compuesto, objeto_imagen):
    elem = ElementoPage(
        title="Test", slug="test-img", thumbnail=objeto_imagen, tipo="imagen"
    )
    elemento_compuesto.add_child(instance=elem)
    assert elem.tipo == "imagen"
    assert elem.thumbnail == objeto_imagen


def test_permite_guardar_texto(elemento_compuesto):
    elem = ElementoPage(
        title="Test", slug="test-texto",
        tipo="texto", contenido_texto="<p>Texto de prueba</p>"
    )
    elemento_compuesto.add_child(instance=elem)
    assert elem.tipo == "texto"
    assert "<p>Texto de prueba</p>" in elem.contenido_texto


def test_permite_guardar_video_externo(elemento_compuesto):
    elem = ElementoPage(
        title="Test", slug="test-video", tipo="video",
        contenido_url="https://www.youtube.com/watch?v=abc"
    )
    elemento_compuesto.add_child(instance=elem)
    assert elem.tipo == "video"
    assert elem.contenido_url == "https://www.youtube.com/watch?v=abc"


def test_permite_guardar_audio_externo(elemento_compuesto):
    elem = ElementoPage(
        title="Test", slug="test-audio", tipo="audio",
        contenido_url="https://soundcloud.com/test"
    )
    elemento_compuesto.add_child(instance=elem)
    assert elem.tipo == "audio"
    assert elem.contenido_url == "https://soundcloud.com/test"


def test_permite_guardar_video_local(elemento_compuesto, objeto_documento_video):
    elem = ElementoPage(
        title="Test", slug="test-video-local", tipo="video",
        contenido_multimedia=objeto_documento_video
    )
    elemento_compuesto.add_child(instance=elem)
    elem.refresh_from_db()

    assert elem.tipo == "video"
    assert elem.contenido_multimedia == objeto_documento_video
    assert elem.contenido_multimedia.title == "documento de video de prueba"


def test_permite_guardar_audio_local(elemento_compuesto, objeto_documento_audio):
    elem = ElementoPage(
        title="Test", slug="test-audio-local", tipo="audio",
        contenido_multimedia=objeto_documento_audio
    )
    elemento_compuesto.add_child(instance=elem)
    elem.refresh_from_db()

    assert elem.tipo == "audio"
    assert elem.contenido_multimedia == objeto_documento_audio
    assert elem.contenido_multimedia.title == "documento de audio de prueba"

def test_contenido_multimedia_puede_ser_none(elemento_compuesto):
    elem = ElementoPage(
        title="Test", slug="test-video-local", tipo="video",
        contenido_multimedia=None
    )
    elemento_compuesto.add_child(instance=elem)
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