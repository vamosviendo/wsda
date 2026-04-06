from django.core.mail import send_mail
from django.template.response import TemplateResponse
from django.db import models
from django.core.validators import RegexValidator
from wagtail.admin.panels import FieldPanel
from wagtail.blocks import CharBlock, RichTextBlock, StructBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

from base.models import ContactSettings
from paginas.forms import ContactForm


class AcercaDePage(Page):
    titulo = models.CharField(max_length=255)
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('titulo'),
        FieldPanel('body'),
    ]


class ContactPage(Page):
    intro = RichTextField(blank=True, verbose_name="Presentación")
    thank_you_text = RichTextField(
        blank=True,
        verbose_name="Texto de agradecimiento"
    )
    to_address = models.EmailField(
        blank=True,
        verbose_name="Dirección de destino",
        help_text="Si se deja vacío se usará la dirección de ContactSettings",
    )


    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('thank_you_text'),
        FieldPanel('to_address'),
    ]

    def serve(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = ContactForm(request.POST)
            if form.is_valid():
                self.send_mail(form)
                context = self.get_context(request)
                context["form"] = None
                return TemplateResponse(
                    request,
                    'paginas/contact_page_landing.html',
                    context,
                )
        else:       # request.method == "GET"
            form = ContactForm()

        context = self.get_context(request)
        context['form'] = form
        return TemplateResponse(
            request,
            self.get_template(request),
            context,
        )

    def send_mail(self, form):
        recipient = self.to_address
        if not recipient:
            contact_settings = ContactSettings.objects.first()
            if contact_settings and contact_settings.email:
                recipient = contact_settings.email

        if not recipient:
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
            recipient_list=[recipient],
            fail_silently=False,
        )


anio_validator = RegexValidator(
    regex=r'^(19|20)\d{2}$',
    message="El año debe estar entre 1900 y 2099"
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
