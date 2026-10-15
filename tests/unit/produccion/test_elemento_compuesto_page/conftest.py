import pytest


@pytest.fixture
def elemento_compuesto_2(elemento_factory, area_page):
    return elemento_factory(
        padre=area_page,
        compuesto=True,
        titulo="Elemento Compuesto 2",
    )
