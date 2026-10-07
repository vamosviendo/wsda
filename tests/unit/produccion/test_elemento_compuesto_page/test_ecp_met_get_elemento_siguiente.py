def test_devuelve_elemento_compuesto_siguiente(elemento_compuesto, elemento_compuesto_2):
    assert elemento_compuesto.get_elemento_siguiente() == elemento_compuesto_2


def test_devuelve_elemento_simple_siguiente(elemento_compuesto, elemento_de_area):
    assert elemento_compuesto.get_elemento_siguiente() == elemento_de_area


def test_devuelve_none_si_no_hay_siguiente(elemento_compuesto_2):
    assert elemento_compuesto_2.get_elemento_siguiente() is None
