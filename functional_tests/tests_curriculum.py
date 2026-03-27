from selenium.webdriver.common.by import By
from wagtail.blocks import StreamValue

from functional_tests.base import FunctionalTestBase
from paginas.models import EntradaCurriculumBlock, CurriculumPage


class CurriculumPageTest(FunctionalTestBase):
    """
    Tests funcionales — Página Curriculum

    Historia que cubre este test:

      El administrador crea una página de curriculum con varias entradas
      (año, título, lugar, nota) y la publica.
      El visitante abre el sitio, encuentra el link en el menú de
      navegación, hace clic y lee las entradas del curriculum.
    """

    def setUp(self):
        super().setUp()
        self.curriculum_page = CurriculumPage(
            title="Curriculum",
            slug="curriculum",
            show_in_menus=True,
            live=True,
        )
        self.homepage.add_child(instance=self.curriculum_page)

    def test_visitante_ve_titulo_de_seccion(self):
        """El visitante ve el encabezado 'Muestras, premios y salones'."""
        self.get(self.curriculum_page.url)
        heading = self.wait_for("h2.page-titulo")
        self.assertIn("Muestras, premios y salones", heading.text)

    def test_curriculum_aparece_en_menu_de_navegacion(self):
        """El visitante encuentra el link al curriculum en el menú de navegación."""
        self.get("/")
        nav = self.wait_for("nav")
        enlaces = nav.find_elements(By.TAG_NAME, "a")
        enlace = next(
            (a for a in enlaces if "curriculum" in a.text.lower()),
            None
        )
        self.assertIsNotNone(
            enlace,
            "El visitante no encontró 'Curriculum' en el menú de navegación"
        )

    def test_visitante_navega_desde_menu_y_ve_contenedor_de_entradas(self):
        """El visitante llega al curriculum desde el menú y ve el contenedor de entradas."""
        self.get("/")
        nav = self.wait_for("nav")
        enlace = next(
            (a for a in nav.find_elements(By.TAG_NAME, "a")
             if "curriculum" in a.text.lower()),
            None
        )
        self.assertIsNotNone(enlace)
        enlace.click()
        self.wait_for(".curriculum-entradas")

    def test_visitante_lee_entrada_publicada(self):
        """El visitante puede leer una entrada con año, título, lugar y nota."""

        block = EntradaCurriculumBlock()
        self.curriculum_page.entradas = StreamValue(
            self.curriculum_page.entradas.stream_block,
            [
                (
                    "entrada",
                    {
                        "anio": "2022",
                        "titulo": "Salón municipal de pintura Gualchi",
                        "lugar": "Exaltación de la Cruz, Provincia de Buenos Aires",
                        "nota": "<p>Primer premio</p>",
                    },
                )
            ],
            is_lazy=False,
        )
        revision = self.curriculum_page.save_revision()
        revision.publish()

        self.get(self.curriculum_page.url)
        self.screenshot("curriculum_con_entrada")

        body_text = self.wait_for("body").text
        self.assertIn("2022", body_text)
        self.assertIn("Salón municipal de pintura Gualchi", body_text)
        self.assertIn("Exaltación de la Cruz", body_text)
        self.assertIn("Primer premio", body_text)

    def test_admin_has_entradas_field(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Crear superuser si no existe
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@test.com',
                password='adminpass'
            )
        self.login_admin(username='admin', password='adminpass')
        self.get(f'/admin/pages/add/paginas/curriculumpage/{self.homepage.pk}/')
        self.assertIn('entradas', self.browser.page_source)
