import pytest

from produccion.models import ElementoPage


def test_elimina_elementos_compuestos_e_hijos_del_area(
        area_page, elemento_compuesto, elemento):
    id = elemento.block_id

    area_page.delete()

    with pytest.raises(ElementoPage.DoesNotExist):
        ElementoPage.objects.get(block_id=id)
