from wagtail.blocks import StructBlock, StreamBlock, URLBlock
from wagtail.images.blocks import ImageBlock


class FranjaBlock(StructBlock):
    imagen = ImageBlock(required=True)
    url = URLBlock(required=True)

    class Meta:
        template = "home/blocks/franja_block.html"


class HomeStreamBlock(StreamBlock):
    franja = FranjaBlock(group="Section")
