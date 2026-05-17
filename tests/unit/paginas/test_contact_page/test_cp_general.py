from unittest.mock import patch

import pytest
from pytest_django import asserts


@pytest.fixture
def contacto_form_data():
    return {
        "nombre": "Juan Perez",
        "email": "juan@test.com",
        "asunto": "Consulta",
        "mensaje": "Hola, necesito información.",
    }


def test_get_muestra_form(contacto_page, client):
    response = client.get(contacto_page.url)
    assert response.status_code == 200
    for campo in ("nombre", "email", "asunto", "mensaje"):
        asserts.assertContains(
            response, f'name="{campo}"',
            msg_prefix=f'Campo "{campo}" ausente'
        )
    asserts.assertContains(response, "Enviar")


def test_post_valido_redirige_a_landing(contacto_page, contacto_form_data, client):
    with patch("paginas.models.send_mail"):
        response = client.post(contacto_page.url, contacto_form_data)
        assert response.status_code == 200
        asserts.assertContains(response, "Gracias por contactar")


def test_post_valido_envia_email(contacto_page, contacto_setting, contacto_form_data, client):
    data = contacto_form_data
    with patch("paginas.models.send_mail") as mock_send_mail:
        client.post(contacto_page.url, contacto_form_data)
        mock_send_mail.assert_called_once_with(
            subject=f"[web] {data['asunto']}",
            message=f"De: {data['nombre']} <{data['email']}>\nAsunto: {data['asunto']}\n\n{data['mensaje']}",
            from_email=data['email'],
            recipient_list=[contacto_setting.email],
            fail_silently=False,
        )

def test_post_invalido_no_envia_email(contacto_page, client):
    with patch("paginas.models.send_mail") as mock_send_mail:
        client.post(contacto_page.url, {})
        mock_send_mail.assert_not_called()


def test_post_con_email_invalido_no_envia_mail(
        contacto_page, client, contacto_form_data):
    contacto_form_data['email'] = "no-es-mail"
    with patch("paginas.models.send_mail") as mock_send_mail:
        client.post(contacto_page.url, contacto_form_data)
        mock_send_mail.assert_not_called()
