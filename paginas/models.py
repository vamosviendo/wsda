from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.blocks import CharBlock, RichTextBlock, StructBlock
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

from base.models import ContactSettings


class AcercaDePage(Page):
    titulo = models.CharField(max_length=255)
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('titulo'),
        FieldPanel('body'),
    ]


anio_validator = RegexValidator(
    regex=r'^(19|20)\d{2}$',
    message="El año debe estar entre 1900 y 2099"
)

class FormField(AbstractFormField):
    page = ParentalKey('ContactPage', on_delete=models.CASCADE, related_name='form_fields')


class ContactPage(AbstractEmailForm):
    intro = RichTextField(blank=True, verbose_name="Presentación")
    thank_you_text = RichTextField(blank=True, verbose_name="Texto de agradecimiento")

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel('intro'),
        InlinePanel('form_fields', label='campos del formulario'),
        FieldPanel('thank_you_text'),
        FieldPanel('to_address'),
    ]

    def send_mail(self, form):
        contact_settings = ContactSettings.objects.first()
        if not contact_settings or not contact_settings.email:
            return

        nombre = form.cleaned_data.get("nombre", "")
        email = form.cleaned_data.get("email", "")
        asunto = form.cleaned_data.get("asunto", "")
        mensaje = form.cleaned_data.get("mensaje", "")

        body = f"De: {nombre} <{email}>\nAsunto: {asunto}\n\n{mensaje}"

        send_mail(
            subject=f"[web] {asunto}",
            message=body,
            from_email=email,
            recipient_list=[contact_settings.email],
            fail_silently=False,
        )


class EntradaCurriculumBlock(StructBlock):
    anio = CharBlock(label="Año", max_length=4, validators=[anio_validator])
    titulo = CharBlock(label="Título", max_length=255)
    lugar = CharBlock(
        label="Lugar / Institución",
        required=False,
        max_length=255,
    )
    nota = RichTextBlock(label="Otros datos", required=False)

    class Meta:
        label = "Entrada"
        icon = "date"


class CurriculumPage(Page):
    entradas = StreamField(
        [("entrada", EntradaCurriculumBlock()),],
        blank=True,
        use_json_field=True,
        verbose_name="Entradas",
    )

    content_panels = Page.content_panels + [
        FieldPanel("entradas"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context["entradas_ordenadas"] = sorted(
            self.entradas,
            key=lambda x: x.value.get("anio", ""),
            reverse=True,
        )

        return context

    class Meta:
        verbose_name = "Página de currículum"
