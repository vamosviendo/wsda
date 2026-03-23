from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from home.models import HomePage
from produccion.models import AreaPage


class HomeSetUpTests(WagtailPageTestCase):
    """
    Tests for basic page structure setup and HomePage creation.
    """

    def test_root_create(self):
        root_page = Page.objects.get(pk=1)
        self.assertIsNotNone(root_page)

    def test_homepage_create(self):
        root_page = Page.objects.get(pk=1)
        homepage = HomePage(title="Home")
        root_page.add_child(instance=homepage)
        self.assertTrue(HomePage.objects.filter(title="Home").exists())


class HomeTests(WagtailPageTestCase):
    """
    Tests for homepage functionality and rendering.
    """

    def setUp(self):
        """
        Create a homepage instance for testing.
        """
        root_page = Page.get_first_root_node()
        Site.objects.create(hostname="testsite", root_page=root_page, is_default_site=True)
        self.homepage = HomePage(title="Home")
        root_page.add_child(instance=self.homepage)

    def test_homepage_is_renderable(self):
        self.assertPageIsRenderable(self.homepage)

    def test_homepage_template_used(self):
        response = self.client.get(self.homepage.url)
        self.assertTemplateUsed(response, "home/home_page.html")


# ============================================================
# 1. TESTS FUNCIONALES
# ============================================================

class HomePageFunctionalTests(WagtailPageTestCase):
    """
    Verifica la experiencia del usuario en la página de inicio:
    qué ve, qué URLs responden, qué estructura HTML recibe.
    """

    def setUp(self):
        root_page = Page.get_first_root_node()
        self.homepage = HomePage(title="Home")
        root_page.add_child(instance=self.homepage)
        self.site_name = "Hilario Ascasubi"
        self.site = Site.objects.create(
            hostname="testsite",
            root_page=self.homepage,
            is_default_site=True,
            site_name=self.site_name,
        )

    # --- Acceso y respuesta HTTP ---

    def test_homepage_returns_200(self):
        """El usuario puede acceder a la página de inicio sin error."""
        response = self.client.get(self.homepage.url)
        self.assertEqual(response.status_code, 200)

    # --- Templates ---

    def test_homepage_uses_home_template(self):
        """La portada usa el template específico de homepage."""
        response = self.client.get(self.homepage.url)
        self.assertTemplateUsed(response, "home/home_page.html")

    def test_homepage_extends_base_template(self):
        """La portada extiende el template base (hereda header, footer, etc.)."""
        response = self.client.get(self.homepage.url)
        self.assertTemplateUsed(response, "base.html")

    def test_homepage_renders_header(self):
        """La portada incluye el partial del header."""
        response = self.client.get(self.homepage.url)
        self.assertTemplateUsed(response, "includes/header.html")

    def test_homepage_renders_footer(self):
        """La portada incluye el partial del footer."""
        response = self.client.get(self.homepage.url)
        self.assertTemplateUsed(response, "includes/footer.html")

    # --- Contenido visible para el usuario ---

    def test_homepage_shows_site_name_in_header(self):
        """El nombre del sitio aparece en el header."""
        response = self.client.get(self.homepage.url)
        self.assertContains(response, self.site_name)

    def test_homepage_has_link_to_root(self):
        """El header tiene un enlace a la raíz del sitio."""
        response = self.client.get(self.homepage.url)
        self.assertContains(response, 'href="/"')

    def test_homepage_shows_inicio_in_nav(self):
        """El menú de navegación tiene el ítem 'Inicio'."""
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "Inicio")

    def test_homepage_shows_blog_link_in_nav(self):
        """El menú tiene el enlace externo al blog."""
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "lilianamedela.blogspot.com")

    def test_homepage_has_franjas_container(self):
        """La portada tiene el contenedor de franjas (aunque esté vacío)."""
        response = self.client.get(self.homepage.url)
        self.assertContains(response, 'class="franjas"')

    def test_homepage_title_present(self):
        """El título de la página aparece en algún lugar del HTML."""
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "Home")

    # --- Navegación hacia páginas hijas ---

    def test_area_page_appears_in_nav_when_in_menu(self):
        """
        Una AreaPage marcada como 'in_menu' aparece en la navegación
        de la portada.
        """
        area = AreaPage(title="Pintura", titulo="Pintura", show_in_menus=True)
        self.homepage.add_child(instance=area)
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "Pintura")

    def test_area_page_not_in_nav_when_not_in_menu(self):
        """
        Una AreaPage NO marcada como 'in_menu' no aparece en la navegación.
        """
        area = AreaPage(title="Oculta", titulo="Oculta", show_in_menus=False)
        self.homepage.add_child(instance=area)
        response = self.client.get(self.homepage.url)
        self.assertNotContains(response, "Oculta")


# ============================================================
# 2. TESTS UNITARIOS
# ============================================================

class HomePageStructureTests(WagtailPageTestCase):
    """Verifica la creación y estructura del modelo HomePage."""

    def test_root_page_exists(self):
        """La raíz de páginas de Wagtail existe tras las migraciones."""
        root_page = Page.objects.get(pk=1)
        self.assertIsNotNone(root_page)

    def test_homepage_can_be_created(self):
        """Se puede crear y persistir un HomePage."""
        root_page = Page.objects.get(pk=1)
        homepage = HomePage(title="Home")
        root_page.add_child(instance=homepage)
        self.assertTrue(HomePage.objects.filter(title="Home").exists())

    def test_homepage_has_body_field(self):
        """HomePage tiene el campo body (StreamField)."""
        homepage = HomePage(title="Test")
        self.assertTrue(hasattr(homepage, "body"))

    def test_homepage_body_empty_by_default(self):
        """El body empieza vacío (sin franjas)."""
        root_page = Page.get_first_root_node()
        homepage = HomePage(title="Test vacío")
        root_page.add_child(instance=homepage)
        self.assertEqual(len(homepage.body), 0)

    def test_homepage_is_renderable(self):
        """Wagtail puede renderizar HomePage sin errores."""
        root_page = Page.get_first_root_node()
        Site.objects.create(
            hostname="testsite",
            root_page=root_page,
            is_default_site=True,
        )
        homepage = HomePage(title="Home")
        root_page.add_child(instance=homepage)
        self.assertPageIsRenderable(homepage)

    def test_homepage_template_path(self):
        """
        El template que usa HomePage es el correcto.
        (Verifica que no se usa el template genérico de Wagtail.)
        """
        root_page = Page.get_first_root_node()
        Site.objects.create(hostname="testsite", root_page=root_page, is_default_site=True)
        homepage = HomePage(title="Home")
        root_page.add_child(instance=homepage)
        response = self.client.get(homepage.url)
        self.assertTemplateUsed(response, "home/home_page.html")
        self.assertTemplateNotUsed(response, "home/welcome_page.html")
