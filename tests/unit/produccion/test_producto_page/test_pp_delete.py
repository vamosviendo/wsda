import pytest

from produccion.models import ElementoPage


def test_al_eliminar_producto_se_eliminan_paginas_hijas(
        producto_page, elemento):
    id = elemento.block_id

    producto_page.delete()

    with pytest.raises(ElementoPage.DoesNotExist):
        ElementoPage.objects.get(block_id=id)
