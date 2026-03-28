from django.core.exceptions import ValidationError
import pytest
from wagtail.admin.panels import get_edit_handler
from wagtail.blocks import StreamValue
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from home.models import HomePage
from paginas.models import CurriculumPage


def crear_sitio(homepage):
    Site.objects.create(
        hostname="testsite",
        root_page=homepage,
        is_default_site=True,
        site_name="Liliana Medela",
    )


class CurriculumPageBase(WagtailPageTestCase):
    def setUp(self):
        root_page = Page.get_first_root_node()
        self.homepage = HomePage(title="Home")
        root_page.add_child(instance=self.homepage)
        crear_sitio(self.homepage)


class CurriculumPageFunctionalTests(CurriculumPageBase):

    def setUp(self):
        super().setUp()
        self.curriculum = CurriculumPage(
            title="Curriculum",
            slug="curriculum",
        )
        self.homepage.add_child(instance=self.curriculum)

    def test_curriculum_page_returns_200(self):
        response = self.client.get(self.curriculum.url)
        self.assertEqual(response.status_code, 200)

    def test_curriculum_page_uses_correct_template(self):
        response = self.client.get(self.curriculum.url)
        self.assertTemplateUsed(response, "paginas/curriculum_page.html")

    def test_curriculum_page_extends_base(self):
        response = self.client.get(self.curriculum.url)
        self.assertTemplateUsed(response, "base.html")

    def test_curriculum_page_shows_heading(self):
        response = self.client.get(self.curriculum.url)
        self.assertContains(response, "Muestras, premios y salones")

    def test_curriculum_page_has_entradas_container(self):
        response = self.client.get(self.curriculum.url)
        self.assertContains(response, 'class="curriculum-entradas"')

    def test_curriculum_page_loads_css(self):
        response = self.client.get(self.curriculum.url)
        self.assertContains(response, "curriculum_page.css")

    def test_curriculum_page_is_renderable(self):
        self.assertPageIsRenderable(self.curriculum)

    def test_curriculum_page_edit_form_has_entradas(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Crear superuser si no existe
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@test.com',
                password='adminpass'
            )

        # Login como staff
        self.client.login(username='admin', password='adminpass')

        # GET a la página de creación
        response = self.client.get(f'/admin/pages/add/paginas/curriculumpage/{self.homepage.pk}/')

        # Verificar que el campo 'entradas' está en el HTML
        self.assertContains(response, 'id="entradas"')


class CurriculumPageUnitTests(CurriculumPageBase):

    def test_curriculum_page_can_be_created(self):
        curriculum = CurriculumPage(title="Curriculum")
        self.homepage.add_child(instance=curriculum)
        self.assertTrue(CurriculumPage.objects.filter(title="Curriculum").exists())

    def test_curriculum_page_has_entradas_field(self):
        curriculum = CurriculumPage(title="Test")
        self.assertTrue(hasattr(curriculum, "entradas"))

    def test_entradas_field_can_contain_entrada_curriculum_block(self):
        from wagtail.blocks import StreamValue

        curriculum = CurriculumPage(title="Test")
        self.homepage.add_child(instance=curriculum)

        stream_value = StreamValue(
            curriculum.entradas.stream_block,
            [
                (
                    "entrada",
                    {
                        "anio": "2022",
                        "titulo": "Salón de pintura",
                        "lugar": "Buenos Aires",
                        "nota": "<p>Premio</p>",
                    }
                )
            ],
            is_lazy=False,
        )
        curriculum.entradas = stream_value
        curriculum.save()

        curriculum.refresh_from_db()
        self.assertEqual(len(curriculum.entradas), 1)
        self.assertEqual(curriculum.entradas[0].block_type, "entrada")

    def test_curriculum_page_entradas_has_panel_in_admin(self):
        edit_handler = get_edit_handler(CurriculumPage)
        panel_names = []
        for panel in edit_handler.children:
            if hasattr(panel, 'bind_to_model'):
                panel_names.append(panel.field_name)
            else:
                panel_names.append(str(panel))
        self.assertIn('entradas', panel_names)

    def test_curriculum_page_entradas_empty_by_default(self):
        curriculum = CurriculumPage(title="Test")
        self.homepage.add_child(instance=curriculum)
        self.assertEqual(len(curriculum.entradas), 0)


class EntradaCurriculumBlockUnitTests(CurriculumPageBase):

    def setUp(self):
        super().setUp()
        self.curriculum = CurriculumPage(title="Test")
        self.homepage.add_child(instance=self.curriculum)

    def test_entrada_curriculum_block_can_save_and_retrieve_fields(self):

        entrada_data = {
            "anio": "2023",
            "titulo": "Exposición anual",
            "lugar": "Museo de Arte",
            "nota": "<p>Participación</p>",
        }

        stream_value = StreamValue(
            self.curriculum.entradas.stream_block,
            [("entrada", entrada_data)],
            is_lazy=False,
        )
        self.curriculum.entradas = stream_value
        self.curriculum.save()
        self.curriculum.refresh_from_db()

        primera_entrada = self.curriculum.entradas[0].value
        self.assertEqual(primera_entrada["anio"], "2023")
        self.assertEqual(primera_entrada["titulo"], "Exposición anual")
        self.assertEqual(primera_entrada["lugar"], "Museo de Arte")
        self.assertIn("Participación", primera_entrada["nota"].source)

    def test_anio_field_validates_year_format(self):
        for anio_invalido in ["23", "20234", "abcd", "1a2b"]:
            print(f"Testeando {anio_invalido}")

            stream_block = self.curriculum.entradas.stream_block
            stream_value = StreamValue(
                stream_block,
                [(
                    "entrada",
                    {
                        "anio": anio_invalido,
                        "titulo": "Test",
                        "lugar": "",
                        "nota": ""}
                )],
                is_lazy=False,
            )

            with self.assertRaises(ValidationError):
                stream_block.clean(stream_value)
