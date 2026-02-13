from wagtail.admin.panels import FieldPanel
from wagtail.models import Page
from wagtail.fields import StreamField

from home.blocks import HomeStreamBlock


class HomePage(Page):
    body = StreamField(
        HomeStreamBlock(),
        blank=True,
        use_json_field=True,
        help_text="Agregue una imagen y una URL para cada sección "
                  "que quiera que aparezca en la portada"
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]
