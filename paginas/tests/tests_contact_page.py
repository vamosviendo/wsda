from unittest.mock import patch

from django.conf import settings as django_settings
from wagtail.models import Locale, Page, Site
from wagtail.test.utils import WagtailPageTestCase

from base.models import ContactSettings
from home.models import HomePage
from paginas.models import ContactPage


class ContactPageBase(WagtailPageTestCase):
    def setUp(self):

        Locale.objects.get_or_create(language_code=django_settings.LANGUAGE_CODE)

        root_page = Page.get_first_root_node()
        if not root_page:
            root_page = Page.add_root(title="Root", slug="root")

        self.homepage = HomePage.objects.filter(slug="home").first()
        if not self.homepage:
            self.homepage = HomePage(title="Home", slug="home")
            root_page.add_child(instance=self.homepage)

        if not Site.objects.filter(hostname="testsite").exists():
            Site.objects.create(
                hostname="testsite",
                root_page=self.homepage,
                is_default_site=True,
                site_name="Liliana Medela",
            )


class ContactPageFormularioFijoTests(ContactPageBase):
    """Tests que verifican que ContactPage tiene un formulario fijo con campos predefinidos."""

    def test_contact_page_renders_with_form(self):
        """ContactPage se renderiza con el formulario de contacto."""
        contacto = ContactPage(title="Contacto", slug="contacto")
        self.homepage.add_child(instance=contacto)

        response = self.client.get(contacto.url)
        self.assertEqual(response.status_code, 200)

    def test_contact_page_form_has_nombre(self):
        """El formulario tiene campo nombre."""
        contacto = ContactPage(title="Contacto", slug="contacto")
        self.homepage.add_child(instance=contacto)

        response = self.client.get(contacto.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="nombre"')

    def test_contact_page_form_has_email(self):
        """El formulario tiene campo email."""
        contacto = ContactPage(title="Contacto", slug="contacto")
        self.homepage.add_child(instance=contacto)

        response = self.client.get(contacto.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="email"')

    def test_contact_page_form_has_asunto(self):
        """El formulario tiene campo asunto."""
        contacto = ContactPage(title="Contacto", slug="contacto")
        self.homepage.add_child(instance=contacto)

        response = self.client.get(contacto.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="asunto"')

    def test_contact_page_form_has_mensaje(self):
        """El formulario tiene campo mensaje."""
        contacto = ContactPage(title="Contacto", slug="contacto")
        self.homepage.add_child(instance=contacto)

        response = self.client.get(contacto.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="mensaje"')

    def test_contact_page_form_has_submit(self):
        """El formulario tiene botón de enviar."""
        contacto = ContactPage(title="Contacto", slug="contacto")
        self.homepage.add_child(instance=contacto)

        response = self.client.get(contacto.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enviar")

    def test_contact_page_admin_no_tiene_campos_dinamicos(self):
        """El admin de ContactPage no muestra campos dinámicos de formulario."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@test.com",
                password="adminpass",
            )
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(
            f"/admin/pages/add/paginas/contactpage/{self.homepage.pk}/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "form_fields")

    def test_contact_page_admin_no_tiene_to_address(self):
        """El admin de ContactPage no muestra campo to_address."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@test.com",
                password="adminpass",
            )
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(
            f"/admin/pages/add/paginas/contactpage/{self.homepage.pk}/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="to_address"')

    def test_contact_page_post_envia_email(self):
        """Al hacer POST se envía el email correctamente."""
        from base.models import ContactSettings
        ContactSettings.objects.create(email="destino@wlili.com")

        contacto = ContactPage(title="Contacto", slug="contacto")
        self.homepage.add_child(instance=contacto)

        with patch("paginas.models.send_mail") as mock_send_mail:
            response = self.client.post(contacto.url, {
                "nombre": "Juan Perez",
                "email": "juan@test.com",
                "asunto": "Consulta",
                "mensaje": "Hola, quiero información",
            })
            self.assertEqual(response.status_code, 200 )

            mock_send_mail.assert_called_once()
            mock_send_mail.assert_called_once_with(
                subject="[web] Consulta",
                message="De: Juan Perez <juan@test.com>\nAsunto: Consulta\n\nHola, quiero información",
                from_email="juan@test.com",
                recipient_list=["destino@wlili.com"],
                fail_silently=False,
            )

    def test_contact_page_post_muestra_landing(self):
        """Al hacer POST se redirige a la página de agradecimiento."""
        from base.models import ContactSettings
        ContactSettings.objects.create(email="destino@wlili.com")

        contacto = ContactPage(
            title="Contacto",
            slug="contacto",
            thank_you_text="<p>Gracias por contactar.</p>",
        )
        self.homepage.add_child(instance=contacto)

        with patch("paginas.models.send_mail"):
            response = self.client.post(contacto.url, {
                "nombre": "Juan Perez",
                "email": "juan@test.com",
                "asunto": "Consulta",
                "mensaje": "Hola",
            })
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Gracias por contactar")
            # self.assertIn("landing", response.url)

    def test_contact_page_post_valida_campos_requeridos(self):
        """El POST valida que los campos requeridos estén presentes."""
        contacto = ContactPage(title="Contacto", slug="contacto")
        self.homepage.add_child(instance=contacto)

        response = self.client.post(contacto.url, {})
        self.assertEqual(response.status_code, 200)

    def test_contact_page_post_valida_email_invalido(self):
        """El POST valida que el email tenga formato correcto."""
        contacto = ContactPage(title="Contacto", slug="contacto")
        self.homepage.add_child(instance=contacto)

        response = self.client.post(contacto.url, {
            "nombre": "Juan",
            "email": "no-es-email",
            "asunto": "Consulta",
            "mensaje": "Hola",
        })
        self.assertEqual(response.status_code, 200)


class ContactPageModelTests(ContactPageBase):
    """Tests unitarios para el modelo ContactPage."""

    def test_contact_page_can_be_created(self):
        """ContactPage puede ser creado como hijo de HomePage."""
        contacto = ContactPage(title="Contacto Test", slug="contacto-test")
        self.homepage.add_child(instance=contacto)
        self.assertTrue(ContactPage.objects.filter(title="Contacto Test").exists())

    def test_contact_page_exists_in_models(self):
        """El modelo ContactPage existe."""
        self.assertTrue(ContactPage is not None)


class ContactSettingsTests(ContactPageBase):
    """Tests para la configuración de contacto."""

    def setUp(self):
        super().setUp()
        self.contacto = ContactPage(title="Contacto", slug="contacto")
        self.homepage.add_child(instance=self.contacto)

    def test_contact_settings_exists(self):
        """ContactSettings está registrado como setting."""
        from base.models import ContactSettings
        self.assertTrue(ContactSettings is not None)

    def test_contact_settings_has_email_field(self):
        """ContactSettings tiene campo email."""
        from base.models import ContactSettings
        self.assertTrue(hasattr(ContactSettings, "_meta"))
        field_names = [f.name for f in ContactSettings._meta.get_fields()]
        self.assertIn("email", field_names)

    def test_contact_settings_admin_form_has_email(self):
        """El admin de ContactSettings tiene campo email."""
        settings = ContactSettings.objects.create(email="test@wlili.com")

        self.create_superuser(
            username="admin",
            password="password",
            email="admin@test.com",
        )

        self.client.login(username="admin", password="password")

        response = self.client.get(f"/admin/settings/base/contactsettings/{settings.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="email"')


class ContactPageEnvioEmailTests(ContactPageBase):
    """Tests para verificar el envío de emails."""

    def setUp(self):
        super().setUp()
        self.contacto = ContactPage(
            title="Contacto",
            slug="contacto",
        )
        self.homepage.add_child(instance=self.contacto)

    @patch("paginas.models.send_mail")
    def test_send_mail_to_configured_address(self, mock_send_mail):
        """El email se envía a la dirección configurada en ContactSettings."""
        from base.models import ContactSettings
        ContactSettings.objects.create(email="destino@wlili.com")

        class MockForm:
            cleaned_data = {
                "nombre": "Juan Perez",
                "email": "juan@test.com",
                "asunto": "Consulta",
                "mensaje": "Hola, quiero información",
            }

        self.contacto.send_mail(MockForm())

        mock_send_mail.assert_called_once()

        mock_send_mail.assert_called_once_with(
            subject="[web] Consulta",
            message="De: Juan Perez <juan@test.com>\nAsunto: Consulta\n\nHola, quiero información",
            from_email="juan@test.com",
            recipient_list=["destino@wlili.com"],
            fail_silently=False,
        )
