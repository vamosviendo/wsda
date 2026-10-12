from django.db import migrations

from utils.db_utils import existe_columna


def borrar_columna(apps, schema_editor):
    cursor = schema_editor.connection.cursor()
    if existe_columna(cursor, "produccion_areapage", "productos"):
        cursor.execute("ALTER TABLE produccion_areapage DROP COLUMN productos")


def revertir(apps, schema_editor):
    raise NotImplementedError(
        "El drop de productos es una limpieza del respaldo crudo. "
        "Para revertir, restaurar desde backup o recrear la columna a mano."
    )


class Migration(migrations.Migration):
    dependencies = [
        ("produccion", "0017_delete_productopage"),
    ]

    operations = [
        migrations.RunPython(borrar_columna, revertir),
    ]
