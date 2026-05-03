import pytest
from django.core.exceptions import ValidationError

from produccion.models import ElementoPage


@pytest.fixture
def elem(test_page, producto_page, objeto_imagen):
    return test_page(
        parent=producto_page,
        page_type=ElementoPage,
        imagen=objeto_imagen,
        title="x",
        slug="x",
    )

def test_unidad_cm_por_defecto(elem):
    assert elem.unidad == "cm"


def test_unidad_de_peso_kg_por_defecto(elem):
    assert elem.unidad_peso == "kg"


def test_debe_tener_imagen(elem):
    elem.imagen = None
    with pytest.raises(ValidationError):
        elem.full_clean()
