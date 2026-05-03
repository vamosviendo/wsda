def test_devuelve_producto_siguiente(producto_page, producto_page_2):
    assert producto_page.get_producto_siguiente() == producto_page_2


def test_devuelve_none_si_no_hay_siguiente(producto_page_2):
    assert producto_page_2.get_producto_siguiente() is None
