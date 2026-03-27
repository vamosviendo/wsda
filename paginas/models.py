from django.db.models import CharField
from wagtail.admin.panels import FieldPanel
from wagtail.blocks import CharBlock, RichTextBlock, StreamBlock, StructBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page


class AcercaDePage(Page):
    titulo = CharField(max_length=255)
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('titulo'),
        FieldPanel('body'),
    ]


class EntradaCurriculumBlock(StructBlock):
    anio = CharBlock(label="Año", max_length=4)
    titulo = CharBlock(label="Título", max_length=255)
    lugar = CharBlock(
        label="Lugar / Institución",
        required=False,
        max_length=255,
    )
    nota = RichTextBlock(label="Otros datos", required=False)


class CurriculumPage(Page):
    entradas = StreamField([
        ("entrada", EntradaCurriculumBlock()),
    ])

    content_panels = Page.content_panels + [
        FieldPanel("entradas"),
    ]
