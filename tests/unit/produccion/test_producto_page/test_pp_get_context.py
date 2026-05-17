from produccion.models import ElementoPage


def test_incluye_elementos_hijos(producto_page, elemento, client):
    response = client.get(producto_page.url)
    assert list(response.context["elementos"]) == [elemento]


def test_respeta_orden_del_arbol(
        producto_page, elemento, elemento_2, elemento_3, client):
    response = client.get(producto_page.url)
    assert list(response.context["elementos"]) == [elemento, elemento_2, elemento_3]


def test_respeta_orden_modificado(
        producto_page, elemento, elemento_2, elemento_3, factory, client):
    elemento_3.move(elemento, pos="left")
    response = client.get(producto_page.url)
    assert list(response.context["elementos"]) == [elemento_3, elemento, elemento_2]


def test_no_incluye_elementos_sin_block_id(
        producto_page, elemento, test_page, objeto_imagen, factory, client):
    """ Los elementos legacy (creados directamente, sin block_id)
        no se incluyen en el context."""
    elemento_legacy = test_page(
        producto_page, ElementoPage, "Elemento legacy", publish=True,
        slug="legacy-sin-block", imagen=objeto_imagen,
        titulo="Legacy sin block"
    )
    assert elemento_legacy.block_id is None

    request = factory.get("/")
    context = producto_page.get_context(request)

    titulos_en_context = [e.titulo for e in context["elementos"] if e]
    assert elemento.titulo in titulos_en_context
    assert "Legacy sin block" not in titulos_en_context
