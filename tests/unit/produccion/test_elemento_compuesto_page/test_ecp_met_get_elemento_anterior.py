def test_devuelve_elemento_compuesto_anterior(elemento_compuesto, elemento_compuesto_2):
    assert elemento_compuesto_2.get_elemento_anterior() == elemento_compuesto


def test_devuelve_elemento_simple_anterior(elemento_de_area, elemento_compuesto):
    assert elemento_compuesto.get_elemento_anterior() == elemento_de_area


def test_devuelve_none_si_no_hay_anterior(elemento_compuesto):
    assert elemento_compuesto.get_elemento_anterior() is None
