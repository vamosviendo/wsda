from django.db import models
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
)
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    register_setting,
)


@register_setting
class NavigationSettings(BaseGenericSetting):
    instagram_url = models.URLField(verbose_name="Instagram URL", blank=True)
    facebook_url = models.URLField(verbose_name="Facebook URL", blank=True)
    x_url = models.URLField(verbose_name="X URL", blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("instagram_url"),
                FieldPanel("facebook_url"),
                FieldPanel("x_url"),
            ],
            "Configuración de redes sociales",
        )
    ]

