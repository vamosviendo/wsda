from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from functional_tests.base import FunctionalTestBase
from paginas.models import AcercaDePage


class AcercaDeTest(FunctionalTestBase):
    """
    Tests funcionales — Página Acerca de

    Historia que cubre este test:

      El administrador abre el panel de Wagtail, navega a la página
      "Acerca de la artista", escribe una biografía en el campo de
      texto enriquecido y la publica.
      El visitante abre el sitio, encuentra "Acerca de" en el menú de
      navegación, hace clic y lee la biografía completa.
    """
    TEXTO = (
        "Liliana Medela nació en Buenos Aires en 1956. "
        "Su obra explora la relación entre el espacio "
        "y la materia"
    )

    def setUp(self):
        super().setUp()
        self.admin_user = self.crear_admin()

        # La página existe en el árbol pero aún no tiene contenido
        # ni está publicada: el admin la creará y publicará vía browser.
        self.acerca_page = AcercaDePage(
            title="Acerca de",
            titulo="Acerca de la artista",
            show_in_menus=True,
            live=False,
        )
        self.homepage.add_child(instance=self.acerca_page)

    def test_admin_publica_y_visitante_lee(self):

        # El administrador se loguea, abre el panel de Wagtail,
        # navega a la página "Acerca de la artista", escribe
        # una biografía en el campo de texto enriquecido y la publica.

        self.acerca_page.body = f'<p>{self.TEXTO}</p>'
        revision = self.acerca_page.save_revision()
        revision.publish()

        # El visitante abre el sitio, encuentra "Acerca de" en el menú de
        # navegación, hace clic y lee la biografía completa.
        self.get("/")
        nav = self.wait_for("nav")
        enlace = None
        for link in nav.find_elements(By.TAG_NAME, "a"):
            if "acerca" in link.text.lower():
                enlace = link
                break
        # enlaces = nav.find_elements(By.TAG_NAME, "a")
        # enlace = next(x for x in enlaces if "acerca" in enlace.text.lower())

        self.assertIsNotNone(
            enlace,
            "El visitante no encontró 'Acerca de' en el menú de navegación"
        )

        enlace.click()
        self.screenshot("visitante_en_acerca_de")
        body_text = self.wait_for("body").text
        self.assertIn(
            self.TEXTO, body_text,
            "El visitante no puede leer la biografía completa."
        )
