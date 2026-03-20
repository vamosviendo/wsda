from django.db import models
import wagtail.blocks
from wagtail.admin.panels import FieldPanel, HelpPanel, MultiFieldPanel
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


class ProductoPage(Page):
    titulo = models.CharField(max_length=255)
    descripcion = RichTextField(blank=True)

    subpage_types = ["produccion.ElementoPage"]

    content_panels = Page.content_panels + [
        FieldPanel("titulo"),
        FieldPanel("descripcion"),
        HelpPanel(
            content=(
                "<p><strong>Gestión de imágenes de la galería:</strong></p>"
                "<ul>"
                "<li><strong>Agregar una imagen:</strong> en el menú de tres puntos (...) "
                "junto al título de esta página, seleccione <em>Añadir página hija</em>.</li>"
                "<li><strong>Cambiar el orden:</strong> desde el mismo menú, "
                "seleccione <em>Ordenar menú</em> y arrastre las imágenes al orden deseado.</li>"
                "</ul>"
                "<p><em>Nota: cada imagen tiene su propia página de detalle donde puede agregarse "
                "agregar título, dimensiones, descripción y comentarios.</em></p>"
            )
        ),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["elementos"] = (
            self.get_children()
            .type(ElementoPage)
            .live()
            .specific()
            .order_by("path")
        )
        return context


class ElementoPage(Page):
    imagen = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    alt_imagen = models.CharField(max_length=255, null=True, blank=True)
    titulo = models.CharField(max_length=255, null=True, blank=True)
    alto = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        verbose_name="Alto"
    )
    ancho = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        verbose_name="Ancho"
    )
    profundidad = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        verbose_name="Profundidad"
    )
    UNIDAD_CHOICES = [
        ("cm", "cm"),
        ("mm", "mm"),
        ("m", "m"),
    ]
    unidad = models.CharField(
        max_length=10, choices=UNIDAD_CHOICES, blank=True, default="cm",
        verbose_name="Unidad de medida"
    )
    peso = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        verbose_name="Profundidad"
    )
    UNIDAD_PESO_CHOICES = [
        ("g", "g"),
        ("kg", "kg"),
    ]
    unidad_peso = models.CharField(
        max_length=10, choices=UNIDAD_PESO_CHOICES, blank=True, default="kg",
        verbose_name="Unidad de peso"
    )
    descripcion = RichTextField(blank=True)
    comentarios = StreamField(
        [("comentario", wagtail.blocks.RichTextBlock())],
        blank=True,
        use_json_field=True,
    )

    parent_page_types = ["produccion.ProductoPage"]

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [FieldPanel("imagen"), FieldPanel("alt_imagen")],
            heading="Imagen",
        ),
        FieldPanel("titulo"),
        MultiFieldPanel(
            [
                FieldPanel("alto"),
                FieldPanel("ancho"),
                FieldPanel("profundidad"),
                FieldPanel("unidad"),
            ],
            heading="Dimensiones",
        ),
        FieldPanel("peso"),
        FieldPanel("descripcion"),
        FieldPanel("comentarios"),
    ]
