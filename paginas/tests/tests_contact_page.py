from unittest.mock import patch

from django.conf import settings as django_settings
from django.contrib.auth import get_user_model
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

        Site.objects.update_or_create(
            hostname="testsite",
            defaults={
                "root_page": self.homepage,
                "is_default_site": True,
                "site_name": "Liliana Medela",
            },
        )


# ============================================================
# 1. TESTS UNITARIOS — ContactPage.serve
# ============================================================

class TestContactPageServe(ContactPageBase):
    """Verifica ContactPage.serve(): GET muestra formulario, POST envía email."""

    def test_get_renderiza_formulario(self):
        contacto = ContactPage(title="Contacto", slug="contacto")
        self.homepage.add_child(instance=contacto)

        response = self.client.get(contacto.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="nombre"')
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="asunto"')
        self.assertContains(response, 'name="mensaje"')
        self.assertContains(response, "Enviar")

    def test_post_valido_redirige_a_landing(self):
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

    def test_post_valido_envia_email(self):
        ContactSettings.objects.create(email="destino@wlili.com")

        contacto = ContactPage(title="Contacto", slug="contacto")
        self.homepage.add_child(instance=contacto)

        with patch("paginas.models.send_mail") as mock_send_mail:
            self.client.post(contacto.url, {
                "nombre": "Juan Perez",
                "email": "juan@test.com",
                "asunto": "Consulta",
                "mensaje": "Hola, quiero información",
            })
            mock_send_mail.assert_called_once_with(
                subject="[web] Consulta",
                message="De: Juan Perez <juan@test.com>\nAsunto: Consulta\n\nHola, quiero información",
                from_email="juan@test.com",
                recipient_list=["destino@wlili.com"],
                fail_silently=False,
            )

    def test_post_invalido_no_envia_email(self):
        contacto = ContactPage(title="Contacto", slug="contacto")
        self.homepage.add_child(instance=contacto)

        with patch("paginas.models.send_mail") as mock_send_mail:
            self.client.post(contacto.url, {})
            mock_send_mail.assert_not_called()

    def test_post_email_invalido_no_envia_email(self):
        contacto = ContactPage(title="Contacto", slug="contacto")
        self.homepage.add_child(instance=contacto)

        with patch("paginas.models.send_mail") as mock_send_mail:
            self.client.post(contacto.url, {
                "nombre": "Juan",
                "email": "no-es-email",
                "asunto": "Consulta",
                "mensaje": "Hola",
            })
            mock_send_mail.assert_not_called()


# ============================================================
# 2. TESTS UNITARIOS — ContactPage.send_mail
# ============================================================

class TestContactPageSendMail(ContactPageBase):
    """Verifica ContactPage.send_mail(): resolución de destinatario."""

    def setUp(self):
        super().setUp()
        self.contacto = ContactPage(title="Contacto", slug="contacto")
        self.homepage.add_child(instance=self.contacto)

    class MockForm:
        cleaned_data = {
            "nombre": "Juan Pérez",
            "email": "juan@test.com",
            "asunto": "Consulta",
            "mensaje": "Hola",
        }

    @patch("paginas.models.send_mail")
    def test_usa_to_address_de_pagina_si_existe(self, mock_send_mail):
        ContactSettings.objects.create(email="settings@wlili.com")

        self.contacto.to_address = "pagina@wlili.com"
        self.contacto.save()

        self.contacto.send_mail(self.MockForm())
        self.assertEqual(mock_send_mail.call_args.kwargs["recipient_list"], ["pagina@wlili.com"])

    @patch("paginas.models.send_mail")
    def test_usa_contact_settings_si_pagina_no_tiene_to_address(self, mock_send_mail):
        ContactSettings.objects.create(email="destino@wlili.com")

        self.contacto.send_mail(self.MockForm())

        self.assertEqual(
            mock_send_mail.call_args.kwargs["recipient_list"],
            ["destino@wlili.com"],
        )

    @patch("paginas.models.send_mail")
    def test_no_envia_si_no_hay_destinatario_configurado(self, mock_send_mail):
        self.contacto.send_mail(self.MockForm())
        mock_send_mail.assert_not_called()


# ============================================================
# 3. TESTS UNITARIOS — ContactSettings (admin)
# ============================================================

class TestContactSettingsAdmin(ContactPageBase):
    """Verifica que ContactSettings tiene campo email en el admin."""

    def setUp(self):
        super().setUp()
        self.settings = ContactSettings.objects.create(email="test@wlili.com")
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@test.com",
                "is_superuser": True,
                "is_staff": True,
            },
        )
        user.set_password("password")
        user.save()
        self.client.login(username="admin", password="password")

    def test_admin_tiene_campo_email(self):
        response = self.client.get(f"/admin/settings/base/contactsettings/{self.settings.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="email"')
