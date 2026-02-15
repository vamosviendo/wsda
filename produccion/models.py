from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

from produccion.blocks import ProduccionStreamBlock


class AreaPage(Page):
    titulo = models.CharField(max_length=255)
    descripcion = RichTextField(blank=True)
    productos = StreamField(
        ProduccionStreamBlock(),
        blank=True,
        use_json_field=True,
        help_text="Agregue una imagen, un nombre y un enlace."
    )

    content_panels = Page.content_panels + [
        FieldPanel("titulo"),
        FieldPanel("descripcion"),
        FieldPanel("productos"),
    ]
