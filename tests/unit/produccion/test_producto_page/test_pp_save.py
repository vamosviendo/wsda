import pytest
from django.test import RequestFactory
from wagtail.blocks import StreamValue

from produccion.models import ElementoPage
from tests.conftest import objeto_imagen


@pytest.fixture
def factory():
    return RequestFactory()


def test_elemento_hijo_existente_sin_block_id_asigna_block_id_al_bloque(
        objeto_imagen, producto_page, factory):
    """
    Cuando hay un ElementoPage hijo existente sin block_id y un bloque en
    StreamField sin block_id que lo reference, _sincronizar_elementos()
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
            "imagen": objeto_imagen,
            "alt_imagen": "Imagen de elemento existente",
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
