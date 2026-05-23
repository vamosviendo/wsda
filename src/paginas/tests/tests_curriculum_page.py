from django.core.exceptions import ValidationError
from wagtail.blocks import StreamValue
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from home.models import HomePage
from paginas.models import CurriculumPage


def crear_sitio(homepage):
    Site.objects.update_or_create(
        hostname="testsite",
        defaults={
            "root_page": homepage,
            "is_default_site": True,
            "site_name": "Liliana Medela",
        },
    )


class CurriculumPageBase(WagtailPageTestCase):
    def setUp(self):
        root_page = Page.get_first_root_node()
        self.homepage = HomePage(title="Home")
        root_page.add_child(instance=self.homepage)
        crear_sitio(self.homepage)


# ============================================================
# 1. TESTS FUNCIONALES — CurriculumPage
# ============================================================

class CurriculumPageFunctionalTests(CurriculumPageBase):

    def setUp(self):
        super().setUp()
        self.curriculum = CurriculumPage(
            title="Curriculum",
            slug="curriculum",
        )
        self.homepage.add_child(instance=self.curriculum)

    def test_curriculum_page_devuelve_200(self):
        response = self.client.get(self.curriculum.url)
        self.assertEqual(response.status_code, 200)

    def test_curriculum_page_usa_template_correcto(self):
        response = self.client.get(self.curriculum.url)
        self.assertTemplateUsed(response, "paginas/curriculum_page.html")

    def test_curriculum_page_extiende_base(self):
        response = self.client.get(self.curriculum.url)
        self.assertTemplateUsed(response, "base.html")

    def test_curriculum_page_muestra_titulo(self):
        response = self.client.get(self.curriculum.url)
        self.assertContains(response, "Muestras, premios y salones")

    def test_curriculum_page_tiene_contenedor_entradas(self):
        response = self.client.get(self.curriculum.url)
        self.assertContains(response, 'class="curriculum-entradas"')

    def test_curriculum_page_carga_css(self):
        response = self.client.get(self.curriculum.url)
        self.assertContains(response, "curriculum_page.css")


# ============================================================
# 2. TESTS UNITARIOS — CurriculumPage.get_context
# ============================================================

class TestCurriculumPageGetContext(CurriculumPageBase):

    def setUp(self):
        super().setUp()
        self.curriculum = CurriculumPage(title="Test", slug="test")
        self.homepage.add_child(instance=self.curriculum)

    def test_entradas_se_muestran_ordenadas_por_anio(self):
        stream_value = StreamValue(
            self.curriculum.entradas.stream_block,
            [
                ("entrada", {"anio": "2020", "titulo": "Primera", "lugar": "", "nota": ""}),
                ("entrada", {"anio": "2023", "titulo": "Tercera", "lugar": "", "nota": ""}),
                ("entrada", {"anio": "2021", "titulo": "Segunda", "lugar": "", "nota": ""}),
            ],
            is_lazy=False,
        )
        self.curriculum.entradas = stream_value
        self.curriculum.save()

        response = self.client.get(self.curriculum.url)
        content = response.content.decode()
        pos_2023 = content.find("2023")
        pos_2021 = content.find("2021")
        pos_2020 = content.find("2020")

        self.assertTrue(pos_2023 < pos_2021 < pos_2020)

    def test_entradas_vacias_no_rompe_context(self):
        response = self.client.get(self.curriculum.url)
        self.assertEqual(response.status_code, 200)


# ============================================================
# 3. TESTS UNITARIOS — EntradaCurriculumBlock.clean
# ============================================================

class TestEntradaCurriculumBlockClean(CurriculumPageBase):

    def setUp(self):
        super().setUp()
        self.curriculum = CurriculumPage(title="Test")
        self.homepage.add_child(instance=self.curriculum)

    def test_anio_valido_es_aceptado(self):
        for anio_valido in ["1900", "1999", "2000", "2023", "2099"]:
            stream_block = self.curriculum.entradas.stream_block
            stream_value = StreamValue(
                stream_block,
                [("entrada", {"anio": anio_valido, "titulo": "Test", "lugar": "", "nota": ""})],
                is_lazy=False,
            )
            stream_block.clean(stream_value)

    def test_anio_invalido_lanza_error_de_validacion(self):
        for anio_invalido in ["23", "20234", "1a2b", "1899", "2100"]:
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
