import pytest

from base.models import FooterText


@pytest.fixture
def footer_text():
    footer = FooterText(body="<p>Texto de footer</p>", live=True)
    footer.save()
    return footer
