from django.db import models
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    PublishingPanel,
)
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    register_setting,
)
from wagtail.fields import RichTextField
from wagtail.models import (
    DraftStateMixin,
    PreviewableMixin,
    RevisionMixin,
    TranslatableMixin,
)
from wagtail.snippets.models import register_snippet


@register_setting
class GeneralSettings(BaseGenericSetting):
    site_title = models.CharField(
        verbose_name="Título del sitio",
        max_length=255,
        blank=True,
    )

    panels = [
        FieldPanel("site_title"),
    ]

    class Meta:
        verbose_name = "configuración general"


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

    class Meta:
        verbose_name = "configuración de redes sociales"


@register_snippet
class FooterText(
    DraftStateMixin,
    RevisionMixin,
    PreviewableMixin,
    TranslatableMixin,
    models.Model,
):
    body = RichTextField()

    panels = [
        FieldPanel("body"),
        PublishingPanel(),
    ]

    def __str__(self):
        return "Texto footer"

    def get_preview_template(self, request, mode_name):
        return "base.html"

    def get_preview_context(self, request, mode_name):
        return {"footer_text": self.body}

    class Meta(TranslatableMixin.Meta):
        verbose_name_plural = "Texto footer"
