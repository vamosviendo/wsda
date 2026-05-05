from produccion.models import ElementoPage


def test_al_modificar_titulo_en_elemento_page_se_modifica_en_block(
        producto_page, elemento, block_elemento):
    elemento.titulo = "Título modificado desde página"
    elemento.save()

    producto_page.refresh_from_db()
    block = producto_page.elementos[0]
    assert block.value.get("titulo") == "Título modificado desde página"


def test_al_modificar_imagen_en_elemento_page_se_actualiza_block(
        producto_page, elemento, block_elemento, objeto_imagen_2):
    elemento.imagen = objeto_imagen_2
    elemento.save()

    producto_page.refresh_from_db()
    block = producto_page.elementos[0]
    assert block.value['imagen'] == objeto_imagen_2


def test_elemento_page_sin_block_id_no_actualiza_padre(
        producto_page, objeto_imagen, test_page):
    """ Un cambio en una ElementoPage legacy (creada directamente, sin
        block_id) no produce cambios en el padre.
    """
    elemento = test_page(
        producto_page, ElementoPage, "Elemento legacy",
        publish=True, titulo="Título", imagen=objeto_imagen
    )

    elemento.titulo = "Nuevo titulo"
    elemento.save()

    producto_page.refresh_from_db()
    assert len(producto_page.elementos) == 0


""" TODO: Agregar test  
    test_elemento_page_solo_puede_crearse_desde_block_en_producto
"""