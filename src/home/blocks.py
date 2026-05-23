from wagtail.blocks import StructBlock, StreamBlock
from wagtail.images.blocks import ImageBlock
from wagtail_link_block.blocks import LinkBlock


class FranjaBlock(StructBlock):
    imagen = ImageBlock(required=True)
    url = LinkBlock()

    class Meta:
        template = "home/blocks/franja_block.html"


class HomeStreamBlock(StreamBlock):
    franja = FranjaBlock(group="Section")
