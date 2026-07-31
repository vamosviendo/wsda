from wagtail.blocks import StreamValue
from wagtail.images import get_image_model

from produccion.models import ElementoPage
from utils.test_utils import get_elemento_block_from_block_id

Image = get_image_model()


def add_elements_to_producto(producto, stream_data):
    producto.elementos = StreamValue(
        producto.elementos.stream_block,
        stream_data,
        is_lazy=False
    )
    producto.save()


def test_al_guardar_producto_con_elementos_de_imagen_se_crean_paginas_hijas(
        producto_page, objeto_imagen, objeto_imagen_2):
    stream_data = [
        ("elemento", {"thumbnail": objeto_imagen, "alt_thumbnail": "Obra 1", "titulo": "Obra número uno"}),
        ("elemento", {"thumbnail": objeto_imagen_2, "alt_thumbnail": "Obra 2", "titulo": "Obra número dos"}),
    ]
    add_elements_to_producto(producto_page, stream_data)

    hijos = producto_page.get_children().specific()
    assert len(hijos) == 2

    titulos = [h.titulo for h in hijos]
    assert titulos == ["Obra número uno", "Obra número dos"]
    thumbnails = [h.thumbnail for h in hijos]
    assert thumbnails == [objeto_imagen, objeto_imagen_2]


def test_al_guardar_producto_con_elementos_de_video_se_crean_paginas_hijas(
        producto_page, objeto_imagen):
    stream_data = [
        ("elemento", {
            "thumbnail": objeto_imagen,
            "alt_thumbnail": "Video",
            "titulo": "Video",
            "tipo": "video",
            "contenido_url": "https://www.youtube.com/watch?v=abc"
        }),
    ]
    add_elements_to_producto(producto_page, stream_data)

    elemento_page = producto_page.get_children().specific().first()
    assert elemento_page.thumbnail == objeto_imagen
    assert elemento_page.alt_thumbnail == "Video"
    assert elemento_page.titulo == "Video"
    assert elemento_page.tipo == "video"
    assert elemento_page.contenido_url == "https://www.youtube.com/watch?v=abc"


def test_al_guardar_producto_con_elementos_de_audio_se_crean_paginas_hijas(
        producto_page, objeto_imagen):
    stream_data = [
        ('elemento', {
            "thumbnail": objeto_imagen,
            "alt_thumbnail": "Audio",
            "titulo": "Elemento de audio",
            "tipo": "audio",
            "contenido_url": "https://soundcloud.com/test"
        }),
    ]
    add_elements_to_producto(producto_page, stream_data)

    elemento_page = producto_page.get_children().specific().first()
    assert elemento_page.tipo == "audio"
    assert elemento_page.contenido_url == "https://soundcloud.com/test"


def test_al_guardar_producto_con_elementos_de_texto_se_crean_paginas_hijas(
        producto_page, objeto_imagen):
    stream_data = [
        ('elemento', {
            "thumbnail": objeto_imagen,
            "alt_thumbnail": "Texto",
            "titulo": "Elemento de texto",
            "tipo": "texto",
            "contenido_texto": "<p>Contenido de texto </p>"
        }),
    ]
    add_elements_to_producto(producto_page, stream_data)

    elemento_page = producto_page.get_children().specific().first()
    assert elemento_page.tipo == "texto"
    assert elemento_page.contenido_texto == "<p>Contenido de texto </p>"


def test_permite_guardar_producto_con_elementos_mixtos(
        producto_page, objeto_imagen):
    stream_data = [
        ("elemento", {
            "thumbnail": objeto_imagen,
            "alt_thumbnail": "Imagen",
            "titulo": "Elemento imagen",
            "tipo": "imagen",
        }),
        ("elemento", {
            "titulo": "Elemento video",
            "contenido_url": "https://soundcloud.com/test"
        }),
        ("elemento", {
            "titulo": "Elemento texto",
            "contenido_texto": "<p>Contenido de texto </p>"
        }),
    ]
    add_elements_to_producto(producto_page, stream_data)

    elementos = producto_page.get_children().specific()
    assert len(elementos) == 3

    titulos = [x.titulo for x in elementos]
    assert titulos == ["Elemento imagen", "Elemento video", "Elemento texto"]


def test_al_modificar_titulo_en_block_se_modifica_en_elemento_page(
        producto_page, elemento, objeto_imagen, block_elemento):
    assert elemento.titulo != "Título modificado"

    stream_data_modificado = [
        ("elemento", {
            "thumbnail": objeto_imagen,
            "alt_thumbnail": block_elemento["alt_thumbnail"],
            "titulo": "Título modificado"
        }),
    ]
    add_elements_to_producto(producto_page, stream_data_modificado)

    elemento.refresh_from_db()
    assert elemento.titulo == "Título modificado"


def test_al_modificar_thumbnail_en_block_se_modifica_en_elemento_page(
        producto_page, elemento, block_elemento, objeto_imagen_2):
    assert elemento.imagen != objeto_imagen_2

    stream_data_modificado = [
        ("elemento", {
            "thumbnail": objeto_imagen_2,
            "alt_thumbnail": block_elemento["alt_thumbnail"],
            "titulo": block_elemento["titulo"]
        }),
    ]
    add_elements_to_producto(producto_page, stream_data_modificado)

    elemento.refresh_from_db()
    assert elemento.imagen == objeto_imagen_2


def test_al_modificar_tipo_en_block_se_modifica_en_elemento_page(
        producto_page, elemento, block_elemento):
    assert elemento.tipo != "audio"

    stream_data_modificado = [
        ("elemento", {
            "thumbnail": block_elemento["thumbnail"],
            "alt_thumbnail": block_elemento["alt_thumbnail"],
            "titulo": block_elemento["titulo"],
            "tipo": "audio",
        }),
    ]
    add_elements_to_producto(producto_page, stream_data_modificado)

    elemento.refresh_from_db()
    assert elemento.tipo == "audio"


def test_al_modificar_contenido_url_en_block_se_modifica_en_elemento_page(
        producto_page, elemento_video, block_elemento_video):
    assert elemento_video.contenido_url != "https://www.youtube.com/watch?v=xyz"

    stream_data_modificado = [
        ("elemento", {
            "thumbnail": block_elemento_video["thumbnail"],
            "alt_thumbnail": block_elemento_video["alt_thumbnail"],
            "titulo": block_elemento_video["titulo"],
            "tipo": block_elemento_video["tipo"],
            "contenido_url": "https://www.youtube.com/watch?v=xyz",
        }),
    ]
    add_elements_to_producto(producto_page, stream_data_modificado)

    elemento_video.refresh_from_db()
    assert elemento_video.contenido_url == "https://www.youtube.com/watch?v=xyz"


def test_al_modificar_contenido_texto_en_block_se_modifica_en_elemento_page(
        producto_page, elemento_texto, block_elemento_texto):
    assert elemento_texto.contenido_texto != "<p>Texto modificado</p>"

    stream_data_modificado = [
        ("elemento", {
            "thumbnail": block_elemento_texto["thumbnail"],
            "alt_thumbnail": block_elemento_texto["alt_thumbnail"],
            "titulo": block_elemento_texto["titulo"],
            "tipo": block_elemento_texto["tipo"],
            "contenido_texto": "<p>Texto modificado</p>"
        }),
    ]
    add_elements_to_producto(producto_page, stream_data_modificado)

    elemento_texto.refresh_from_db()
    assert elemento_texto.contenido_texto == "<p>Texto modificado</p>"


def test_al_eliminar_block_se_elimina_elemento_page(
        producto_page, elemento, elemento_2, block_elemento):
    block_2 = get_elemento_block_from_block_id(
        producto_page, elemento_2.block_id
    )

    assert producto_page.get_children().count() == 2

    stream_data_reducido = [("elemento", block_2)]

    add_elements_to_producto(producto_page, stream_data_reducido)

    assert producto_page.get_children().count() == 1
    hijo = producto_page.get_children().specific().first()
    assert hijo.titulo == elemento_2.titulo


def test_al_modificar_titulo_en_elemento_page_se_modifica_en_block(
        producto_page, elemento, block_elemento):
    elemento.titulo = "Título modificado desde página"
    elemento.save()

    producto_page.refresh_from_db()
    block = producto_page.elementos[0]
    assert block.value.get("titulo") == "Título modificado desde página"


def test_elemento_hijo_existente_sin_block_id_asigna_block_id_al_block(
        objeto_imagen, producto_page, factory):
    """
    Cuando hay un ElementoPage hijo existente sin block_id y un bloque en
    StreamField sin block_id que lo referencie, _sincronizar_elementos()
    debe asignar un block_id al bloque para que get_context() pueda
    encontrar el elemento.
    """
    # Crear un ElementoPage hijo SIN block_id (simula elemento legacy)
    elemento_hijo = ElementoPage(
        title="Elemento existente",
        slug="elemento-ya-existente",
        imagen=objeto_imagen,
        titulo="Elemento existente",
        block_id=None,
    )
    producto_page.add_child(instance=elemento_hijo)

    # Ahora agregamos un bloque que referencia ese elemento
    stream_data = [
        ("elemento", {
            "thumbnail": objeto_imagen,
            "alt_thumbnail": "Imagen de elemento existente",
            "titulo": "Elemento existente",
            "block_id": "",
        }),
    ]

    producto_page.elementos = StreamValue(
        producto_page.elementos.stream_block,
        stream_data,
        is_lazy=False
    )
    producto_page.save()

    bloque = producto_page.elementos[0]
    block_id_del_bloque = bloque.value.get("block_id")
    assert block_id_del_bloque is not None
    assert block_id_del_bloque != ""
    assert block_id_del_bloque != "  "

    request = factory.get("/")
    context = producto_page.get_context(request)
    assert context["elementos"][0] is not None
    assert context["elementos"][0].titulo == "Elemento existente"


def test_producto_sin_elementos_no_tiene_hijos(producto_page):
    add_elements_to_producto(producto_page, [])
    assert producto_page.get_children().count() == 0


def test_si_un_block_elemento_no_tiene_imagen_elemento_page_tampoco(
        producto_page):
    stream_data = [
        ('elemento', {'thumbnail': None, 'alt_thumbnail': "Sin imagen", 'titulo': "Sin imagen"})
    ]
    add_elements_to_producto(producto_page, stream_data)

    hijos = producto_page.get_children().specific()
    assert len(hijos) == 1
    assert hijos[0].imagen is None
