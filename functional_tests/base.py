from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from wagtail.models import Collection, Locale, Page, Site

from home.models import HomePage

class FunctionalTestBase(StaticLiveServerTestCase):
    """
    Clase base para todos los tests de Selenium.
    Gestiona el ciclo de vida del browser y la fixture mínima del sitio.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        # options.add_argument("--headless")        # sin ventana visible en CI/CD
        options.add_argument("--width=1280")
        options.add_argument("--height=900")
        cls.browser = webdriver.Firefox(options=options)
        cls.browser.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        """
        Crea la estructura mínima de Wagtail para cada test:
        Site (hostname = live_server_url) → HomePage

        Nota sobre TransactionTestCase:
        StaticLiveServerTestCase hereda de TransactionTestCase, que hace un
        flush completo de la base de datos entre tests (a diferencia de TestCase,
        que usa rollback). Ese flush borra también la página raíz que Wagtail
        crea en su migración inicial, así que hay que recrearla si no existe.
        """
        # 1. Locale. Necesario para poder crear páginas
        Locale.objects.get_or_create(language_code=settings.LANGUAGE_CODE)

        # 2. Página raíz del árbol de Wagtail
        root_page = Page.objects.filter(depth=1).first() \
                    or Page.add_root(title="Root", slug="root")

        # Si quedaron hijos de un setUp anterior fallido, los borramos.
        for child in root_page.get_children():
            child.delete()
        root_page.refresh_from_db()

        # 3. Colección raíz: necesaria para guardar imágenes de Wagtail
        if not Collection.objects.filter(depth=1).exists():
            Collection.add_root(name="Root")

        self.homepage = HomePage(title="Home", slug="home")
        root_page.add_child(instance=self.homepage)

        self.site_name = "Rogelio Roldán"
        self.site = Site.objects.create(
            # El Site apunta a homepage, no a root_page.
            # Wagtail sirve la página que es root_page del Site;
            # si apuntara al nodo raíz del árbol, el browser mostraría "Root".
            hostname=self._get_hostname(),
            port=self._get_port(),
            root_page=self.homepage,
            is_default_site=True,
            site_name=self.site_name,
        )

    def _get_hostname(self):
        """Extrae el hostname de la URL del servidor de test."""
        return self.live_server_url.replace("http://", "").split(":")[0]

    def _get_port(self):
        """Extrae el puerto de la URL del servidor de test."""
        parts = self.live_server_url.replace("http://", "").split(":")
        return int(parts[1]) if len(parts) > 1 else 80

    def get(self, path="/"):
        """Navega a una ruta relativa del servidor de test."""
        self.browser.get(f"{self.live_server_url}{path}")

    def wait_for(self, css_selector, timeout=5):
        """Espera hasta que un selector CSS esté presente en el DOM."""
        return WebDriverWait(self.browser, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )

    def wait_for_text(self, css_selector, text, timeout=5):
        return WebDriverWait(self.browser, timeout).until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, css_selector), text
            )
        )

    def image_loaded(self, img_element):
        """
        Devuelve True si la imagen fue descargada y renderizada correctamente.
        naturalWidth === 0 significa que el browser no pudo cargar el archivo.
        Este es el test que el cliente HTTP de Django NO puede hacer.
        """
        return self.browser.execute_script(
            "return arguments[0].naturalWidth > 0", img_element
        )

    def element_is_visible(self, css_selector):
        """Verifica que un elemento existe Y es visible en la página."""
        try:
            element = self.browser.find_element(By.CSS_SELECTOR, css_selector)
            return element.is_displayed()
        except Exception:
            return False

    def get_computed_style(self, element, prop):
        """Devuelve el valor de una propiedad CSS computada (interpretada por el browser)."""
        return self.browser.execute_script(
            f"return window.getComputedStyle(arguments[0]).{prop}", element
        )

    def screenshot(self, nombre="debug"):
        path = f"./tmp/selenium_{nombre}.png"
        self.browser.save_screenshot(path)
        print(f"Screenshot guardado: {path}")

    # ── Helpers de administración ────────────────────────────────────

    def crear_admin(self, username="admin", password="adminpass"):
        """Crea un superusuario para los tests que interactúan con el admin."""
        return User.objects.create_superuser(
            username=username,
            password=password,
            email="admin@test.com",
        )

    def login_admin(self, username="admin", password="adminpass"):
        """Abre el panel de Wagtail e inicia sesión."""
        self.browser.get(f"{self.live_server_url}/admin/")
        self.wait_for("#id_username").send_keys(username)
        self.browser.find_element(By.ID, "id_password").send_keys(password)
        self.browser.find_element(By.CSS_SELECTOR, "[type=submit]").click()
        # Espera a que se cargue el dashboard
        self.wait_for(".sidebar")

    def logout_admin(self):
        self.browser.get(f"{self.live_server_url}/admin/logout/")