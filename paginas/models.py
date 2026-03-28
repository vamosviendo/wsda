from django.core.validators import RegexValidator
from django.db.models import CharField
from wagtail.admin.panels import FieldPanel
from wagtail.blocks import CharBlock, RichTextBlock, StructBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page


class AcercaDePage(Page):
    titulo = CharField(max_length=255)
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('titulo'),
        FieldPanel('body'),
    ]


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
