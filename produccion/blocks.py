from wagtail.blocks import StructBlock, CharBlock, StreamBlock, RichTextBlock
from wagtail.images.blocks import ImageBlock
from wagtail_link_block.blocks import LinkBlock


class ElementoBlock(StructBlock):
    imagen = ImageBlock(required=False)
    alt_imagen = CharBlock(required=False, max_length=255)
    titulo = CharBlock(required=False, max_length=255)
    block_id = CharBlock(required=False, max_length=36)

    class Meta:
        template = "produccion/blocks/elemento_block.html"
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
