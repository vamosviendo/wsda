# Migración de DATOS.
#  - Cada ProductoPage se convierte en ElementoPage compuesta, conservando
#    su posición en el árbol (se reutiliza la misma fila de wagtailcore_page;
#    los elementos hijos no se mueven).
#  - Los ProductoBlock de AreaPage.productos se convierten en ElementoBlock
#    dentro de AreaPage.elementos, enlazados por block_id a la página
#    convertida.
# ⚠️ Debe correr ANTES de 0017_delete_productopage. No es reversible:
#    hacer `make data-backup` antes.
import json
import uuid

from django.db import migrations


def convertir(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    ct_elemento = ContentType.objects.get(
        app_label="produccion", model="elementopage"
    )

    cursor = schema_editor.connection.cursor()

    # 0. Leer tarjetas de todas las áreas para rescatar su descripción e imagen.
    descripcion_tarjeta = {}    # page_id -> html de la tarjeta
    imagen_tarjeta = {}
    cursor.execute("SELECT page_ptr_id, productos FROM produccion_areapage")
    areas_raw = cursor.fetchall()

    for _, productos_raw in areas_raw:
        tarjetas = json.loads(productos_raw) if productos_raw else []
        for tarjeta in tarjetas:
            if tarjeta.get("type") != "producto":
                continue
            valor = tarjeta["value"]
            page_id = (valor.get("link") or {}).get("page")
            if not page_id:
                continue
            if page_id not in descripcion_tarjeta:
                descripcion_tarjeta[page_id] = valor.get("descripcion") or ""
            img = valor.get("imagen") or {}
            if page_id not in imagen_tarjeta:
                imagen_tarjeta[page_id] = (img.get("image"), img.get("alt_text") or "")

    # 1. produccion_productopage -> produccion_elementopage (una fila por página)
    cursor.execute(
        "SELECT page_ptr_id, titulo, descripcion, elementos FROM produccion_productopage"
    )
    productos = cursor.fetchall()

    block_ids = {}  # page_id -> block_id nuevo (enlace área <-> página)

    for page_ptr_id, titulo, descripcion, elementos in productos:
        block_id = str(uuid.uuid4())
        block_ids[page_ptr_id] = block_id
        card = descripcion_tarjeta.get(page_ptr_id, "")
        descripcion_final = (card or "") + (descripcion or "")
        thumb_pk, thumb_alt = imagen_tarjeta.get(page_ptr_id, (None, ""))

        cursor.execute(
            """
            INSERT INTO produccion_elementopage
                (page_ptr_id, tipo, titulo, descripcion, comentarios,
                 elementos, block_id, thumbnail_id, alt_thumbnail,
                 contenido_multimedia_id, contenido_texto, contenido_url,
                 compuesto)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [
                page_ptr_id,
                "imagen",           # tipo neutro (es compuesto)
                titulo,
                descripcion_final,
                "[]",
                elementos or "[]",  # JSON crudo: mismo formato de bloques
                block_id,
                thumb_pk,
                thumb_alt,
                None, "", "",
                True,               # compuesto = True
            ],
        )

    for pk in block_ids:
        cursor.execute(
            "UPDATE wagtailcore_page SET content_type_id = %s WHERE id = %s",
            [ct_elemento.id, pk],
        )

    # 2. Tarjetas del área (productosa) -> bloques 'elemento' del área
    for area_page_ptr_id, productos_raw in areas_raw:
        tarjetas = json.loads(productos_raw) if productos_raw else []
        if not tarjetas:
            continue

        nuevos_bloques = []
        for tarjeta in tarjetas:
            if tarjeta.get("type") != "producto":
                nuevos_bloques.append(tarjeta)  # no debería ocurrir; conservar tal cual
                continue
            valor = tarjeta["value"]
            page_id = (valor.get("link") or {}).get("page")
            if not page_id or page_id not in block_ids:
                continue    # link externo / página inexistente -> se saltea
            imagen = valor.get("imagen") or {}
            nuevos_bloques.append({
                "type": "elemento",
                "id": str(uuid.uuid4()),    # id interno del bloque (wagtail)
                "value": {
                    "compuesto": True,
                    "thumbnail": imagen.get("image"),   # JSON crudo: pk int de la imagen
                    "alt_thumbnail": imagen.get("alt_text") or "",
                    "tipo": "imagen",
                    "contenido_url": "",
                    "contenido_multimedia": None,
                    "contenido_texto": "",
                    "titulo": valor.get("nombre") or "",
                    "block_id": block_ids[page_id],     # Enlaza el bloque con la página convertida
                },
            })

        cursor.execute(
            "UPDATE produccion_areapage SET elementos = %s WHERE page_ptr_id = %s",
            [json.dumps(nuevos_bloques), area_page_ptr_id],
        )


def revertir(apps, schema_editor):
    raise NotImplementedError(
        "La conversión ProductoPage->ElementoPage genera block_ids y cambia "
        "content_type; no es reversible. Restaurar desde backup."
    )


class Migration(migrations.Migration):

    dependencies = [
        ("produccion", "0015_elementopage_elementos_alter_areapage_elementos_and_more"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        # Retira 'productos' del ESTADO del modelo sin borrar la columna física
        # (que queda como respaldo crudo en la DB).
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RemoveField(model_name="areapage", name="productos"),
            ],
        ),
        migrations.RunPython(convertir, revertir),
    ]
