from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
    TextBlock,
    URLBlock,
)
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageBlock
from wagtail_link_block.blocks import LinkBlock


TIPO_CHOICES = [
    ('imagen', 'Imagen'),
    ('video', 'Video'),
    ('audio', 'Audio'),
    ('texto', 'Texto'),
]


class ElementoBlock(StructBlock):
    thumbnail = ImageBlock(required=False)
    alt_thumbnail = CharBlock(required=False, max_length=255)
    tipo = ChoiceBlock(
        choices=TIPO_CHOICES,
        default="imagen",
        required=False
    )
    contenido_url = URLBlock(required=False)
    contenido_multimedia = DocumentChooserBlock(required=False,)
    contenido_texto = TextBlock(required=False)
    titulo = CharBlock(required=False, max_length=255)
    block_id = CharBlock(required=False, max_length=36)

    class Meta:
        template = "produccion/blocks/elemento_block.html"
        form_template = "produccion/blocks/elemento_block_form.html"
        icon = "image"


class ElementosStreamBlock(StreamBlock):
    elemento = ElementoBlock(group="Galería")


class ProductoBlock(StructBlock):
    nombre = CharBlock()
    descripcion = RichTextBlock(required=False)
    imagen = ImageBlock()
    link = LinkBlock()

    class Meta:
        template = "produccion/blocks/producto_block.html"


class ProduccionStreamBlock(StreamBlock):
    producto = ProductoBlock(group="Section")
