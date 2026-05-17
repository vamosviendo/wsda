def test_block_id_de_pagina_coincide_con_el_de_el_block(
        producto_page, elemento):
    block = producto_page.elementos[0]
    page = producto_page.get_children().specific().first()

    assert block.value.get("block_id") is not None
    assert page.block_id is not None
    assert block.value.get("block_id") == str(page.block_id)


def test_unidad_cm_por_defecto(elemento):
    assert elemento.unidad == "cm"


def test_unidad_de_peso_kg_por_defecto(elemento):
    assert elemento.unidad_peso == "kg"
