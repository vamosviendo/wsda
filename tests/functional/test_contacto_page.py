import pytest
from selenium.webdriver.common.by import By

from paginas.models import ContactPage


@pytest.fixture
def contacto_page(test_page):
    return test_page(
        page_type=ContactPage,
        title="Contacto",
        slug="contacto",
        thank_you_text="<p>Gracias por contactar. Su mensaje ha sido enviado.</p>",
    )


def test_contacto_page_funciona_correctamente(browser, contacto_page):
    # La página contacto carga sin errores
    browser.get_page(contacto_page.url)
    assert "Contacto" in browser.title

    # Al cargar la página se encuentra un formulario
    form = browser.wait_for("form",  By.TAG_NAME)
    assert form is not None

    # El formulario tiene campos nombre, email, asunto, mensaje y un botón
    # submit
    nombre = browser.find_element(By.NAME, "nombre")
    assert nombre is not None
    email = browser.find_element(By.NAME, "email")
    assert email is not None
    asunto = browser.find_element(By.NAME, "asunto")
    assert asunto is not None
    mensaje = browser.find_element(By.NAME, "mensaje")
    assert mensaje is not None
    boton = browser.find_element(By.CSS_SELECTOR, "button[type=submit]")
    assert boton is not None

    # Al completar y enviar el formulario se muestra mensaje de éxito
    # con un texto de agradecimiento
    nombre.send_keys("Juan Pérez")
    email.send_keys("juan@test.com")
    asunto.send_keys("Consulta")
    mensaje.send_keys("Hola. Quiero info")
    boton.click()

    success_message = browser.wait_for(".success", timeout=10)
    assert success_message.is_displayed()
    assert "gracias" in success_message.text.lower()


def test_valida_formulario(browser, contacto_page):
    browser.get_page(contacto_page.url)
    browser.wait_for("button[type=submit]").click()
    assert "contacto" in browser.current_url

    browser.find_element(By.NAME, "nombre").send_keys("Test")
    browser.find_element(By.NAME, "email").send_keys("no-es-email")
    browser.find_element(By.NAME, "asunto").send_keys("Test")
    browser.find_element(By.NAME, "mensaje").send_keys("Test")
    browser.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    assert "contacto" in browser.current_url
