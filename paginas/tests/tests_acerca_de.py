from django.urls import reverse
from wagtail.test.utils import WagtailPageTestCase
from wagtail.test.utils.form_data import rich_text, nested_form_data

from home.models import HomePage
from paginas.models import AcercaDePage
from utils.test_utils import crear_estructura_basica


class AcercaDePageModelTests(WagtailPageTestCase):
    def setUp(self):
        _, self.homepage = crear_estructura_basica(self)
        self.texto = (
            "Rogelio Roldán nació en Buenos Aires en 1956. "
            "Su obra explora la relación entre el espacio "
            "y la materia"
        )

    def test_puede_crearse_y_persistirse(self):
        page = AcercaDePage(title="Acerca de", titulo="Acerca de la artista")
        self.homepage.add_child(instance=page)
        self.assertTrue(AcercaDePage.objects.filter(titulo="Acerca de la artista").exists())

    def test_puede_guardar_texto(self):
        page = AcercaDePage(
            title="Acerca de",
            titulo="Acerca del artista",
            body=self.texto
        )
        self.homepage.add_child(instance=page)

        self.assertEqual(page.body, self.texto)

    def test_devuelve_200(self):
        page = AcercaDePage(title="Acerca de", titulo="Acerca de la artista")
        self.homepage.add_child(instance=page)
        response = self.client.get(page.url)
        self.assertEqual(response.status_code, 200)

    def test_aparece_en_menu_cuando_show_in_menus_es_true(self):
        page = AcercaDePage(
            title="Acerca de",
            titulo="Acerca de la artista",
            show_in_menus=True,
        )
        self.homepage.add_child(instance=page)
        response = self.client.get(self.homepage.url)
        self.assertContains(response, "Acerca de")

    def test_muestra_titulo_y_body(self):
        page = AcercaDePage(
            title="Acerca de",
            titulo="Acerca del artista",
            body=self.texto
        )
        self.homepage.add_child(instance=page)
        response = self.client.get(page.url)
        self.assertContains(response, "Acerca del artista")
        self.assertContains(response, self.texto)


class AcercaDePageAdminTests(WagtailPageTestCase):

    def setUp(self):
        _, self.homepage = crear_estructura_basica(self)
        self.user = self.create_superuser(
            username="admin",
            password="password",
            email="admin@test.com",
        )
        self.client.login(username="admin", password="password")

    def _url_creacion(self):
        return reverse(
            "wagtailadmin_pages:add",
            args=["paginas", "acercadepage", self.homepage.pk],
        )

    def test_admin_url_de_creacion_es_accesible(self):
        """El formulario de creación de AcercaDePage carga sin errores."""
        response = self.client.get(self._url_creacion())
        self.assertEqual(response.status_code, 200)

    def test_puede_crearse_desde_el_admin_sin_error(self):
        """
        Crear una AcercaDePage desde el admin no produce ValidationError.
        Reproduce el error observado en el servidor de desarrollo.
        """
        self.assertCanCreate(
            self.homepage,
            AcercaDePage,
            nested_form_data({
                "title": "Acerca de",
                "titulo": "Acerca del artista",
                "body": rich_text("<p>Texto de prueba</p>")
            }),
        )

    def test_puede_ser_subpagina_de_homepage(self):
        """AcercaDePage puede crearse como hija de HomePage."""
        self.assertCanCreateAt(HomePage, AcercaDePage)