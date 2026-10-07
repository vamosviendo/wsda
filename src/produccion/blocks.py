from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    StreamBlock,
    StructBlock,
    TextBlock,
    URLBlock, BooleanBlock,
)
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageBlock


TIPO_CHOICES = [
    ('imagen', 'Imagen'),
    ('video', 'Video'),
    ('audio', 'Audio'),
    ('texto', 'Texto'),
]


class ElementoBlock(StructBlock):
    compuesto = BooleanBlock(required=False)
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
