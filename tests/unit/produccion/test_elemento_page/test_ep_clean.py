import pytest
from django.core.exceptions import ValidationError
from wagtail.blocks import StreamValue

from produccion.blocks import ElementosStreamBlock


def _stream_con_un_sub_elemento():
    return StreamValue(
        ElementosStreamBlock(),
        [("elemento", {"titulo": "sub-elemento"})],
        is_lazy=False,
    )


def test_elemento_simple_con_sub_elementos_lanza_validation_error(elemento):
    elemento.elementos = _stream_con_un_sub_elemento()

    with pytest.raises(ValidationError) as exc_info:
        elemento.clean()

    assert "elementos" in exc_info.value.message_dict


def test_elemento_simple_sin_sub_elementos_no_lanza(elemento):
    assert not elemento.elementos

    assert elemento.clean() is None


def test_elemento_compuesto_con_sub_elementos_no_lanza(elemento_compuesto, elemento):
    assert elemento_compuesto.elementos
    assert elemento_compuesto.compuesto is True

    assert elemento_compuesto.clean() is None