import pytest
from django.test import RequestFactory
from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file

from utils.test_utils import get_elemento_block_from_block_id


Image = get_image_model()

@pytest.fixture
def block_elemento(elemento_compuesto, elemento):
    return get_elemento_block_from_block_id(elemento_compuesto, elemento.block_id)


@pytest.fixture
def block_elemento_video(elemento_compuesto, elemento_video):
    return get_elemento_block_from_block_id(elemento_compuesto, elemento_video.block_id)


@pytest.fixture
def block_elemento_texto(elemento_compuesto, elemento_texto):
    return get_elemento_block_from_block_id(elemento_compuesto, elemento_texto.block_id)


@pytest.fixture
def objeto_imagen_2(root_collection):
    image = Image(title="segunda imagen de prueba")
    image.file = get_test_image_file()
    image.save()
    return image


@pytest.fixture
def factory():
    return RequestFactory()
