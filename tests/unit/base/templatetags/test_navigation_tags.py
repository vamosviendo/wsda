from base.templatetags.navigation_tags import get_footer_text


def test_usa_footer_text_de_context_si_existe():
    result = get_footer_text({"footer_text": "<p>Tomado de context</p>"})
    assert result["footer_text"] == "<p>Tomado de context</p>"


def test_consulta_db_si_context_no_tiene_footer_text(footer_text):
    result = get_footer_text({})
    assert result["footer_text"] == footer_text.body


def test_devuelve_vacio_si_no_hay_footer_text_live(footer_text):
    footer_text.live = False
    footer_text.save()
    result = get_footer_text({})
    assert result["footer_text"] == ""
