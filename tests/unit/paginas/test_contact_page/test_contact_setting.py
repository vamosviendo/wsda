from pytest_django import asserts


def test_tiene_campo_email(contacto_setting, authenticated_client):
    response = authenticated_client.get(f"/admin/settings/base/contactsettings/{contacto_setting.pk}/")
    assert response.status_code == 200
    asserts.assertContains(response, 'name="email"')
