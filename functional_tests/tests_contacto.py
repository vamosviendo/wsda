from selenium.webdriver.common.by import By

from functional_tests.base import FunctionalTestBase
from paginas.models import ContactPage


class ContactoPageFunctionalTests(FunctionalTestBase):
    """
    Tests funcionales de la página de contacto con Selenium.
    """

    def setUp(self):
        super().setUp()

        self.contacto = ContactPage(
            title="Contacto",
            slug="contacto",
            thank_you_text="<p>Gracias por contactar. Su mensaje ha sido enviado.</p>",
        )
        self.homepage.add_child(instance=self.contacto)

    # === Tests de carga ===

    def test_contacto_page_loads(self):
        """La página de contacto carga sin errores."""
        self.get(self.contacto.url)
        self.assertIn("Contacto", self.browser.title)

    def test_contacto_page_has_form(self):
        """La página contiene un formulario."""
        self.get(self.contacto.url)
        form = self.browser.find_element(By.TAG_NAME, "form")
        self.assertIsNotNone(form)

    # === Tests de campos ===

    def test_contacto_form_has_nombre_field(self):
        """El formulario tiene campo nombre."""
        self.get(self.contacto.url)
        campo = self.browser.find_element(By.NAME, "nombre")
        self.assertIsNotNone(campo)

    def test_contacto_form_has_email_field(self):
        """El formulario tiene campo email."""
        self.get(self.contacto.url)
        campo = self.browser.find_element(By.NAME, "email")
        self.assertIsNotNone(campo)

    def test_contacto_form_has_asunto_field(self):
        """El formulario tiene campo asunto."""
        self.get(self.contacto.url)
        campo = self.browser.find_element(By.NAME, "asunto")
        self.assertIsNotNone(campo)

    def test_contacto_form_has_mensaje_field(self):
        """El formulario tiene campo mensaje."""
        self.get(self.contacto.url)
        campo = self.browser.find_element(By.NAME, "mensaje")
        self.assertIsNotNone(campo)

    def test_contacto_form_has_submit_button(self):
        """El formulario tiene botón de enviar."""
        self.get(self.contacto.url)
        boton = self.browser.find_element(By.CSS_SELECTOR, "button[type=submit]")
        self.assertIsNotNone(boton)

    # === Tests de envío ===

    def test_contacto_form_shows_success_on_submit(self):
        """Al enviar el formulario se muestra mensaje de éxito."""
        self.get(self.contacto.url)

        self.browser.find_element(By.NAME, "nombre").send_keys("Juan Perez")
        self.browser.find_element(By.NAME, "email").send_keys("juan@test.com")
        self.browser.find_element(By.NAME, "asunto").send_keys("Consulta")
        self.browser.find_element(By.NAME, "mensaje").send_keys("Hola, quiero info")

        self.browser.find_element(By.CSS_SELECTOR, "button[type=submit]").click()

        self.wait_for(".success", timeout=10)
        self.assertTrue(self.element_is_visible(".success"))

    def test_contacto_form_shows_thank_you_text(self):
        """Después de enviar se muestra el texto de agradecimiento."""
        self.get(self.contacto.url)

        self.browser.find_element(By.NAME, "nombre").send_keys("Test")
        self.browser.find_element(By.NAME, "email").send_keys("test@test.com")
        self.browser.find_element(By.NAME, "asunto").send_keys("Test")
        self.browser.find_element(By.NAME, "mensaje").send_keys("Test")

        self.browser.find_element(By.CSS_SELECTOR, "button[type=submit]").click()

        self.wait_for(".success", timeout=10)
        # Verifica que aparece el texto de thank_you_text
        success_text = self.browser.find_element(By.CSS_SELECTOR, ".success")
        self.assertIn("gracias", success_text.text.lower())

    def test_contacto_form_validates_required_fields(self):
        """El formulario valida campos requeridos."""
        self.get(self.contacto.url)

        # Enviar sin completar
        self.browser.find_element(By.CSS_SELECTOR, "button[type=submit]").click()

        # No debe cambiar de página (queda en el formulario)
        self.assertIn("contacto", self.browser.current_url)

    def test_contacto_form_validates_email_format(self):
        """El formulario valida formato de email."""
        self.get(self.contacto.url)

        self.browser.find_element(By.NAME, "nombre").send_keys("Test")
        self.browser.find_element(By.NAME, "email").send_keys("no-es-email")
        self.browser.find_element(By.NAME, "asunto").send_keys("Test")
        self.browser.find_element(By.NAME, "mensaje").send_keys("Test")

        self.browser.find_element(By.CSS_SELECTOR, "button[type=submit]").click()

        # No debe cambiar de página (validación HTML5)
        self.assertIn("contacto", self.browser.current_url)
