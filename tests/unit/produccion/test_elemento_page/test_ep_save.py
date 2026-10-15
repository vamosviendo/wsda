from produccion.models import ElementoPage


def test_al_modificar_titulo_en_elemento_page_se_modifica_en_block(
        elemento_compuesto, elemento, block_elemento):
    elemento.titulo = "Título modificado desde página"
    elemento.save()

    elemento_compuesto.refresh_from_db()
    block = elemento_compuesto.elementos[0]
    assert block.value.get("titulo") == "Título modificado desde página"


def test_al_modificar_thumbnail_en_elemento_page_se_actualiza_block(
        elemento_compuesto, elemento, block_elemento, objeto_imagen_2):
    elemento.imagen = objeto_imagen_2
    elemento.save()

    elemento_compuesto.refresh_from_db()
    block = elemento_compuesto.elementos[0]
    assert block.value['thumbnail'] == objeto_imagen_2


def test_elemento_page_sin_block_id_no_actualiza_padre(
        elemento_compuesto, objeto_imagen, test_page):
    """ Un cambio en una ElementoPage legacy (creada directamente, sin
        block_id) no produce cambios en el padre.
    """
    elemento = test_page(
        elemento_compuesto, ElementoPage, "Elemento legacy",
        publish=True, titulo="Título", imagen=objeto_imagen
    )

    elemento.titulo = "Nuevo titulo"
    elemento.save()

    elemento_compuesto.refresh_from_db()
    assert len(elemento_compuesto.elementos) == 0


def test_al_modificar_contenido_multimedia_en_elemento_page_se_actualiza_block(
        elemento_compuesto, elemento, objeto_documento_video):
    elemento.contenido_multimedia = objeto_documento_video
    elemento.save()

    elemento_compuesto.refresh_from_db()
    block = elemento_compuesto.elementos[0]
    assert block.value['contenido_multimedia'] == objeto_documento_video


def test_al_marcar_elemento_page_como_compuesto_se_actualiza_block(
        elemento_compuesto, elemento):
    assert elemento.compuesto is False

    elemento.compuesto = True
    elemento.save()

    elemento_compuesto.refresh_from_db()
    block = elemento_compuesto.elementos[0]
    assert block.value['compuesto'] is True



""" TODO: Agregar test  
    test_elemento_page_solo_puede_crearse_desde_block_en_producto
"""
