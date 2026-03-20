from wagtail.blocks import StructBlock, CharBlock, StreamBlock, RichTextBlock
from wagtail.images.blocks import ImageBlock
from wagtail_link_block.blocks import LinkBlock


class ProductoBlock(StructBlock):
    nombre = CharBlock()
    descripcion = RichTextBlock(required=False)
    imagen = ImageBlock()
    link = LinkBlock()

    class Meta:
        template = "produccion/blocks/producto_block.html"


class ProduccionStreamBlock(StreamBlock):
    producto = ProductoBlock(group="Section")
