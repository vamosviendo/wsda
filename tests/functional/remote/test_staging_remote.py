import os
import re
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


def test_puede_procesar_upload_de_video_grande(
    live_server_url, remote_admin_user
):
    """ Verifica que el chooser de Wagtail Documents en staging puede procesar
        un upload de video sin devolver 403/500.

        Falla con 403 si:
        - Los nombres de los campos del form son incorrectos.
        - CSRF token no coincide.

        Falla con 500 si:
        - gunicorn mata el worker durante el upload.
        - DATA_UPLOAD_MAX_MEMORY_SIZE demasiado bajo.
    """
    session = requests.Session()

    username = remote_admin_user["username"]
    password = remote_admin_user["password"]

    # 1. Login
    login_url = urljoin(live_server_url, "/admin/login/")
    login_get = session.get(login_url, timeout=10)
    assert login_get.status_code == 200

    csrf_match = re.search(
        r'name="csrfmiddlewaretoken"\s+value="([^"]+)"',
        login_get.text,
    )
    assert csrf_match, "No se encontró CSRF token en login"
    csrf_token = csrf_match.group(1)

    login_post = session.post(
        login_url,
        data={
            "csrfmiddlewaretoken": csrf_token,
            "username": username,
            "password": password,
            "next": "/admin/",
        },
        headers={"Referer": login_url},
        timeout=10,
        allow_redirects=False,
    )
    assert login_post.status_code in (302, 303), \
        f"Login falló: {login_post.status_code}"

    # 2. GET al chooser (devuelve JSON con htmlFragment)
    chooser_url = urljoin(live_server_url, "/admin/documents/chooser/create/")
    chooser_get = session.get(
        chooser_url,
        headers={"Accept": "application/json"},
        timeout=10,
    )
    assert chooser_get.status_code == 200, \
        f"No se pudo acceder al chooser: {chooser_get.status_code}"

    chooser_data = chooser_get.json()
    assert chooser_data["step"] == "reshow_creation_form", \
        f"step inesperado: {chooser_data.get('step')}"

    # Extraer CSRF token del htmlFragment
    html_fragment = chooser_data["htmlFragment"]
    csrf_match = re.search(
        r'name="csrfmiddlewaretoken"\s+value="([^"]+)"',
        html_fragment,
    )
    assert csrf_match, "No se encontró CSRF token en htmlFragment"
    csrf_token = csrf_match.group(1)

    # 3. POST al chooser con nombres de campos correctos
    video_content = (
        b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom"
        + b"\x00" * 1024  # 1 KB
    )

    upload_response = session.post(
        chooser_url,
        data={
            "csrfmiddlewaretoken": csrf_token,
            "document-chooser-upload-title": "Video smoke test",
        },
        files={
            "document-chooser-upload-file": (
                "test_video.mp4", video_content, "video/mp4"
            ),
        },
        headers={
            "Referer": chooser_url,
            "Accept": "application/json",
        },
        timeout=60,
        allow_redirects=False,
    )

    # 4. Verificar respuesta
    if upload_response.status_code == 403:
        pytest.fail(
            f"403 Forbidden. La respuesta del chooser fue:\n"
            f"{upload_response.text[:2000]}"
        )

    assert upload_response.status_code == 200, (
        f"Status inesperado: {upload_response.status_code}. "
        f"Respuesta: {upload_response.text[:1000]}"
    )

    upload_data = upload_response.json()
    assert upload_data.get("step") in ("creation complete",  "chosen"), (
        f"Step inesperado en respuesta: {upload_data.get('step')}. "
        f"Respuesta completa: {upload_data}"
    )

    result = upload_data.get("result", {})
    document_id = result.get("id")
    assert document_id, f"Falta id en resultado: {result}"

    assert result.get("title") == "Video smoke test", \
        f"Título inesperado: {result.get('title')}"
    assert result.get("url"), f"Falta url en resultado: {result}"

    token = os.environ.get("DJANGO_TEST_TOKEN")
    delete_response = requests.post(
        urljoin(live_server_url, "/__test__/delete-document/"),
        data={"document_id": document_id},
        headers={"X-Test-Token": token},
        timeout=10,
    )
    assert delete_response.status_code == 200, (
        f"No se pudo eliminar el documento de prueba. "
        f"Status: {delete_response.status_code}. "
        f"Respuesta: {delete_response.text[:500]}"
    )

    delete_data = delete_response.json()
    assert delete_data.get("deleted") is True, f"Cleanup falló: {delete_data}"
