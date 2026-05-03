def test_devuelve_producto_anterior(producto_page, producto_page_2):
    assert producto_page_2.get_producto_anterior() == producto_page


def test_devuelve_none_si_no_hay_anterior(producto_page):
    assert producto_page.get_producto_anterior() is None
