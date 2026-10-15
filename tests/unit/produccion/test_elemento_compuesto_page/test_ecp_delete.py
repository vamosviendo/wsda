import pytest

from produccion.models import ElementoPage


def test_al_eliminar_producto_se_eliminan_paginas_hijas(
        elemento_compuesto, elemento):
    id = elemento.block_id

    elemento_compuesto.delete()

    with pytest.raises(ElementoPage.DoesNotExist):
        ElementoPage.objects.get(block_id=id)
