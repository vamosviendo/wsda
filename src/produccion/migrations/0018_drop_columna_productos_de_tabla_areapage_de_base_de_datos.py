from django.db import migrations


# TODO Repetida de migration 0016. ¿Extraer a utils?
def _existe_columna(cursor, tabla, columna):
    """ Devuelve true si columna existe en tabla."""
    if cursor.db.vendor == "sqlite":
        cursor.execute(f"PRAGMA table_info({tabla})")
        return any(row[1] == columna for row in cursor.fetchall())

    cursor.execute(
        "SELECT 1 FROM information_schema.columns WHERE table_name = %s AND column_name = %s",
        [tabla, columna],
    )
    return cursor.fetchone() is not None


def borrar_columna(apps, schema_editor):
    cursor = schema_editor.connection.cursor()
    if _existe_columna(cursor, "produccion_areapage", "productos"):
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
