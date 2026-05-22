import os
from urllib.parse import urljoin

import pytest
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.support.wait import WebDriverWait

pytestmark = pytest.mark.skipif(
    not os.environ.get("TEST_SERVER"),
    reason="Smoke tests remotos: requieren TEST_SERVER",
)


def test_staging_sitio_admin_y_static_responden(live_server_url):
    # 1. Sitio remoto es accesible
    home_response = requests.get(live_server_url, timeout=10)
    assert home_response.status_code == 200

    # 2. Admin remoto es accesible
    admin_response = requests.get(
        urljoin(live_server_url, "admin/login/"),
        timeout=10
    )
    assert admin_response.status_code == 200
    assert "password" in admin_response.text.lower()

    # 3. Hay acceso a los recursos static
    soup = BeautifulSoup(home_response.text, "html.parser")

    static_urls = []

    for link in soup.select("link[href]"):
        href = link["href"]
        if "/static/" in href:
            static_urls.append(urljoin(live_server_url, href))

    for script in soup.select("script[src]"):
        src = script["src"]
        if "/static/" in src:
            static_urls.append(urljoin(live_server_url, src))

    assert static_urls, "La homepage no referencia ninún recurso static"

    static_response = requests.get(static_urls[0], timeout=10)
    assert static_response.status_code == 200


def test_staging_admin_login_funciona(browser, remote_admin_user):
    username = remote_admin_user["username"]
    password = remote_admin_user["password"]

    browser.get_page("/admin/login/")

    username_input = browser.wait_for("input[name=username]")
    password_input = browser.wait_for("input[name=password]")

    username_input.clear()
    username_input.send_keys(username)
    password_input.clear()
    password_input.send_keys(password)

    browser.wait_for("button[type=submit]").click()

    WebDriverWait(browser, 10).until(
        lambda driver: (
            "/admin/login" not in driver.current_url
            # or "error" in driver.find_element(By.TAG_NAME, "body").text.lower()
            # or "contraseña" in driver.find_element(By.TAG_NAME, "body").text.lower()
            # or "password" in driver.find_element(By.TAG_NAME, "body").text.lower()
        )
    )

    body = browser.wait_for("body")
    body_text = body.text.lower()

    assert "/admin/login/" not in browser.current_url, (
        "El login no salió de la página de login. "
        f"URL actual: {browser.current_url}. "
        f"Texto visible: {body.text}"
    )

    assert (
        "dashboard" in body_text
        or "panel" in body_text
        or "páginas" in body_text
        or "pages" in body_text
    ), (
        "El login salió de la página de login, pero no llegó claramene "
        f"al dashboard de Wagtail. URL actual: {browser.current_url}. "
        f"Texto visible: {body.text}"
    )

def test_staging_puede_escribir_db_y_media(live_server_url):
    token = os.environ.get("DJANGO_TEST_TOKEN")

    assert token, "Falta definir DJANGO_TEST_TOKEN"

    response = requests.post(
        urljoin(live_server_url, "/__test__/deployment-smoke/"),
        headers={"X-Test-Token": token},
        timeout=20,
    )
    assert response.status_code == 200

    data = response.json()

    assert data["database_write"] == "ok"
    assert data["database_read"] == "ok"
    assert data["media_write"] == "ok"
    assert data["media_read"] == "ok"

    media_url = urljoin(live_server_url, data["media_url"])
    media_response = requests.get(media_url, timeout=10)

    assert media_response.status_code == 200
    assert media_response.content == data["expected_media_content"].encode()
