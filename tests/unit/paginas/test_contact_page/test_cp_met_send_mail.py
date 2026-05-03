import pytest

from unittest.mock import patch


@pytest.fixture
def mock_form():
    class MockForm:
        cleaned_data = {
            "nombre": "Juan Pérez",
            "email": "juan@test.com",
            "asunto": "Consulta",
            "mensaje": "Hola",
        }
    return MockForm()


@patch("paginas.models.send_mail")
def test_usa_to_address_de_pagina_si_existe(
        mock_send_mail, contacto_setting, contacto_page, mock_form):
    contacto_page.to_address = "pagina@wlili.com"
    contacto_page.save()

    contacto_page.send_mail(mock_form)
    assert mock_send_mail.call_args.kwargs["recipient_list"] == ["pagina@wlili.com"]


@patch("paginas.models.send_mail")
def test_usa_contact_setting_si_pagina_no_tiene_to_address(
        mock_send_mail, contacto_setting, contacto_page, mock_form):
    contacto_page.send_mail(mock_form)
    assert mock_send_mail.call_args.kwargs["recipient_list"] == [contacto_setting.email]


@patch("paginas.models.send_mail")
def test_no_envia_si_no_hay_to_address_configurado(mock_send_mail, contacto_page, mock_form):
    contacto_page.send_mail(mock_form)
    mock_send_mail.assert_not_called()


@patch("paginas.models.send_mail")
def test_devuelve_resultado_de_send_mail(mock_send_mail, contacto_setting, contacto_page, mock_form):
    mock_send_mail.return_value = 5
    assert contacto_page.send_mail(mock_form) == 5
