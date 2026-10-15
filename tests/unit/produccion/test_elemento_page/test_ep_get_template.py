def test_devuelve_template_segun_tipo(elemento, elemento_compuesto, request):
    assert elemento.get_template(request) == "produccion/elemento_page.html"
    assert elemento_compuesto.get_template(request) == "produccion/elemento_compuesto_page.html"
