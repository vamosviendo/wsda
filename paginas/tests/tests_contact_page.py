from unittest.mock import patch

from django.conf import settings
from django.conf import settings as django_settings
from wagtail.models import Locale, Page, Site
from wagtail.test.utils import WagtailPageTestCase

from base.models import ContactSettings
from home.models import HomePage
from paginas.models import ContactPage, FormField


def crear_sitio(homepage):
    Site.objects.create(
        hostname="testsite",
        root_page=homepage,
        is_default_site=True,
        site_name="Liliana Medela",
    )


class ContactPageBase(WagtailPageTestCase):
    def setUp(self):

        Locale.objects.get_or_create(language_code=django_settings.LANGUAGE_CODE)

        root_page = Page.get_first_root_node()

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


class ContactPageModelTests(ContactPageBase):
    """Tests unitarios para el modelo ContactPage."""

    def setUp(self):
        super().setUp()
        self.contacto = ContactPage(title="Contacto", slug="contacto")
        self.homepage.add_child(instance=self.contacto)

        # Crear campos del formulario
        for name, field_type, label in [
            ("nombre", "singleline", "Nombre"),
            ("email", "email", "Email"),
            ("asunto", "singleline", "Asunto"),
            ("mensaje", "multiline", "Mensaje"),
        ]:
            FormField.objects.create(
                page=self.contacto,
                field_type=field_type,
                label=label,
                required=True,
            )

    def test_contact_page_can_be_created(self):
        """ContactPage puede ser creado como hijo de HomePage."""
        from paginas.models import ContactPage

        contacto = ContactPage(title="Contacto Test", slug="contacto-test")
        self.homepage.add_child(instance=contacto)
        self.assertTrue(ContactPage.objects.filter(title="Contacto Test").exists())

    def test_contact_page_exists_in_models(self):
        """El modelo ContactPage existe."""
        from paginas.models import ContactPage
        self.assertTrue(ContactPage is not None)

    def test_contact_page_form_has_email_field(self):
        """El formulario público tiene campo email."""
        response = self.client.get(self.contacto.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="email"')

    def test_contact_page_form_has_nombre_field(self):
        """El formulario público tiene campo nombre."""
        response = self.client.get(self.contacto.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="nombre"')

    def test_contact_page_form_has_asunto_field(self):
        """El formulario público tiene campo asunto."""
        response = self.client.get(self.contacto.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="asunto"')

    def test_contact_page_form_has_mensaje_field(self):
        """El formulario público tiene campo mensaje."""
        response = self.client.get(self.contacto.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="mensaje"')


class ContactSettingsTests(ContactPageBase):
    """Tests para la configuración de contacto."""

    def setUp(self):
        super().setUp()
        from paginas.models import ContactPage
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

    def test_contact_page_edit_form_has_to_address(self):
        """El formulario de ContactPage en admin tiene campo to_address."""
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
        self.assertContains(response, 'name="to_address"')


class ContactPageEnvioEmailTests(ContactPageBase):
    """Tests para verificar el envío de emails."""

    def setUp(self):
        super().setUp()
        self.contacto = ContactPage(
            title="Contacto",
            slug="contacto",
            to_address="destino@test.com",
        )
        self.homepage.add_child(instance=self.contacto)
        # Crear campos del formulario
        for name, field_type, label in [
            ("nombre", "singleline", "Nombre"),
            ("email", "email", "Email"),
            ("asunto", "singleline", "Asunto"),
            ("mensaje", "multiline", "Mensaje"),
        ]:
            FormField.objects.create(
                page=self.contacto,
                field_type=field_type,
                label=label,
                required=True,
            )

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
