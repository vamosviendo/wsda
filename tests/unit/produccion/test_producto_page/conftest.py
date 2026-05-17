import pytest

from produccion.models import ProductoPage


@pytest.fixture
def producto_page_2(test_page, area_page):
    return test_page(
        parent=area_page,
        page_type=ProductoPage,
        title="ProductoPage",
        titulo="Producto Page 2",
        descripcion="Página de producto 2",
    )
