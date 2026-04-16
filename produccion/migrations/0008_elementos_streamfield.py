from django.db import migrations, models
from wagtail.fields import StreamField
import produccion.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('produccion', '0007_alter_elementopage_peso'),
    ]

    operations = [
        migrations.AddField(
            model_name='elementopage',
            name='block_id',
            field=models.UUIDField(null=True, blank=True, editable=False),
        ),
        migrations.AddField(
            model_name='productopage',
            name='elementos',
            field=StreamField(
                [
                    ('elemento', produccion.blocks.ElementoBlock()),
                ],
                blank=True,
                use_json_field=True,
                help_text='Agregue imágenes a la galería del producto.',
            ),
        ),
    ]