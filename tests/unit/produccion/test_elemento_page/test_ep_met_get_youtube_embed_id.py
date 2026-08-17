import pytest

from produccion.models import ElementoPage

ID_TEST = "dwm1aOS6-pw"
URL_TEST = f"https://www.youtube.com/watch?v={ID_TEST}"
URL_CORTA = f"https://youtu.be/{ID_TEST}"
URL_EMBED = f"https://www.youtube.com/embed/{ID_TEST}"


@pytest.fixture
def elemento_v():
    return ElementoPage(
        title="Video test",
        slug="video-test",
        tipo="video",
    )


def test_devuelve_none_si_contenido_url_vacio(elemento_v):
    """ Si contenido_url está vacío devuelve None"""
    elemento_v.contenido_url = ""
    assert elemento_v.get_youtube_embed_id() is None


def test_devuelve_none_si_contenido_url_no_es_youtube(elemento_v):
    """ Si el contenido_url no es de youtube devuelve None"""
    elemento_v.contenido_url = "https://www.vimeo.com/123456"
    assert elemento_v.get_youtube_embed_id() is None


def test_extrae_id_de_url_youtu_be_simple(elemento_v):
    """ youtu.be/VIDEO_ID -> VIDEO_ID"""
    elemento_v.contenido_url = URL_CORTA
    assert elemento_v.get_youtube_embed_id() == ID_TEST


def test_extrae_id_de_url_youto_be_con_parametros(elemento_v):
    """ youtu.be/VIDEO_ID?s1=... -> VIDEO_ID (ignora parámetros)"""
    elemento_v.contenido_url = f"{URL_CORTA}?si=2d5C_gk82PL4Hv7s"
    assert elemento_v.get_youtube_embed_id() == ID_TEST


def test_extrae_id_de_url_youtube_watch(elemento_v):
    """ youtube.com/watch?v=VIDEO_ID -> VIDEO_ID"""
    elemento_v.contenido_url = URL_TEST
    assert elemento_v.get_youtube_embed_id() == ID_TEST


def test_extrae_id_de_url_youtube_watch_con_parametros(elemento_v):
    """youtube.com/watch?v=VIDEO_ID&si=... → VIDEO_ID."""
    elemento_v.contenido_url = f"{URL_TEST}&si=2d5C_gk82PL4Hv7s"
    assert elemento_v.get_youtube_embed_id() == ID_TEST


def test_extrae_id_de_url_youtube_embed(elemento_v):
    """youtube.com/embed/VIDEO_ID → VIDEO_ID."""
    elemento_v.contenido_url = URL_EMBED
    assert elemento_v.get_youtube_embed_id() == ID_TEST


def test_extrae_id_con_guiones_y_guion_bajo(elemento_v):
    """El ID de YouTube puede contener guiones y guion bajo."""
    elemento_v.contenido_url = f"https://youtu.be/abc_DEF-123"
    assert elemento_v.get_youtube_embed_id() == "abc_DEF-123"
