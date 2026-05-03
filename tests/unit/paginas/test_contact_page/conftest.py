import pytest

from base.models import ContactSettings
from paginas.models import ContactPage


@pytest.fixture
def contacto_page(test_page):
    return test_page(
        page_type=ContactPage,
        title="Contacto",
        slug="contacto",
        thank_you_text="<p>Gracias por contactar</p>"
    )


@pytest.fixture
def contacto_setting():
    return ContactSettings.objects.create(email="destino@wlili.com")
