import os
from urllib.parse import urljoin

import pytest
import requests
from django.urls import reverse
from selenium.webdriver.firefox.options import Options

from tests.functional.base import MiFirefox


@pytest.fixture(scope="session")
def browser(live_server_url):
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--width=1280")
    options.add_argument("--height=900")
    driver = MiFirefox(options=options, base_url=live_server_url)
    driver.implicitly_wait(5)
    yield driver
    driver.close()


@pytest.fixture
def remote_admin_user(live_server_url):
    token = os.environ.get("DJANGO_TEST_TOKEN")
    username = os.environ.get("DJANGO_TEST_ADMIN_USERNAME", "admin")
    password = os.environ.get("DJANGO_TEST_ADMIN_PASSWORD", "adminpassword")

    assert token, "Falta definir DJANGO_TEST_TOKEN"

    response = requests.post(
        urljoin(live_server_url, "/__test__/admin-user/"),
        headers={"X-Test-Token": token},
        timeout=10,
    )

    assert response.status_code == 200, (
        f"No se puedo crear el admin remoto. Status: {response.status_code}. "
        f"URL: {response.url}. Respuesta: {response.text[:2000]}"
    )
    data = response.json()
    assert data["username"] == username

    try:
        yield {
            "username": username,
            "password": password,
        }
    finally:
        response = requests.delete(
            urljoin(live_server_url, reverse("remote-test-admin")),
            headers={"X-Test-Token": token},
            timeout=10,
        )
        assert response.status_code == 200, (
            "No se pudo eliminar el admin remoto. "
            f"Status: {response.status_code}. URL: {response.url}. "
            f"Respuesta: {response.text[:500]}"
        )
