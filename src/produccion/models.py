from __future__ import annotations

import uuid
from typing import Self

from django.db import models
from django.templatetags.static import static
from django.utils.text import slugify
import wagtail.blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.embeds.embeds import get_embed
from wagtail.embeds.exceptions import EmbedException
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.blocks import StreamValue

from produccion.blocks import ProduccionStreamBlock, ElementosStreamBlock

TIPO_CHOICES = [
    ('imagen', 'Imagen'),
    ('video', 'Video'),
    ('audio', 'Audio'),
    ('texto', 'Texto'),
]


class AreaPage(Page):
    titulo = models.CharField(max_length=255)
    descripcion = RichTextField(blank=True)
    productos = StreamField(
        ProduccionStreamBlock(),
        blank=True,
        use_json_field=True,
        help_text="Agregue una imagen, un nombre y un enlace."
    )

    content_panels = Page.content_panels + [
        FieldPanel("titulo"),
        FieldPanel("descripcion"),
        FieldPanel("productos"),
    ]


class ProductoPage(Page):
    titulo = models.CharField(max_length=255)
    descripcion = RichTextField(blank=True)
    elementos = StreamField(
        ElementosStreamBlock(),
        blank=True,
        use_json_field=True,
        help_text="Agregue imágenes a la galería del producto."
    )

    subpage_types = ["produccion.ElementoPage"]

    content_panels = Page.content_panels + [
        FieldPanel("titulo"),
        FieldPanel("descripcion"),
        FieldPanel("elementos"),
    ]

    def save(self, *args, **kwargs):
        if getattr(self, '_syncing_from_block', False):
            super().save(*args, **kwargs)
            return

        bypass_sync = kwargs.pop('bypass_sync', False)
        super().save(*args, **kwargs)

        if bypass_sync:
            return

        if self.elementos:
            self._sincronizar_elementos()

    def _sincronizar_elementos(self):
        elementos_db = {
            str(e.block_id): e
            for e in self.get_children().specific()
            if e.block_id
        }

        hijos_por_orden = list(
            self.get_children()
            .type(ElementoPage)
            .specific()
            .order_by('path')
        )

        nuevos_blocks = []
        block_ids_en_streamfield = set()
        posicion_actual = 0

        for block in self.elementos:
            block_value = dict(block.value)
            block_id = block_value.get('block_id')

            if not block_id:
                if posicion_actual < len(hijos_por_orden):
                    elemento_existente = hijos_por_orden[posicion_actual]
                    if elemento_existente.block_id:
                        block_id = str(elemento_existente.block_id)
                        block_value['block_id'] = block_id
                        self._actualizar_elemento_si_necesario(elemento_existente, block_value)
                    else:
                        block_id = str(uuid.uuid4())
                        block_value['block_id'] = block_id
                        elemento_existente._syncing_from_block = True
                        elemento_existente.block_id = block_id
                        elemento_existente.save()
                        self._actualizar_elemento_si_necesario(elemento_existente, block_value)
                else:
                    block_id = str(uuid.uuid4())
                    block_value['block_id'] = block_id
                    self._crear_elemento(block_value)
                block_value['block_id'] = block_id
            elif str(block_id) not in elementos_db:
                self._crear_elemento(block_value)
            else:
                elemento = elementos_db[str(block_id)]
                self._actualizar_elemento_si_necesario(elemento, block_value)

            block_ids_en_streamfield.add(str(block_id))
            nuevos_blocks.append(('elemento', block_value))
            posicion_actual += 1

        elementos_a_eliminar = [
            elemento for elemento in hijos_por_orden
            if elemento.block_id and str(elemento.block_id) not in block_ids_en_streamfield
        ]
        for elemento in elementos_a_eliminar:
            self._eliminar_elemento(elemento)

        self.elementos = StreamValue(
            stream_block=self._meta.get_field('elementos').stream_block,
            stream_data=nuevos_blocks,
            is_lazy=False
        )
        Page.save(self, update_fields=['elementos'])

    def _crear_elemento(self, block_value):
        titulo = block_value.get('titulo') or 'Sin título'
        thumbnail = block_value.get('thumbnail')
        alt_thumbnail = block_value.get('alt_thumbnail')
        tipo = block_value.get("tipo", "imagen")
        contenido_url = block_value.get("contenido_url", "")
        contenido_texto = block_value.get("contenido_texto", "")
        block_id = block_value.get('block_id')

        slug_base = slugify(titulo) if titulo else 'elemento'
        slug = slug_base
        counter = 1
        while self.get_children().filter(slug=slug).exists():
            slug = f"{slug_base}-{counter}"
            counter += 1

        elemento = ElementoPage(
            title=titulo,
            slug=slug,
            thumbnail=thumbnail,
            alt_thumbnail=alt_thumbnail,
            titulo=titulo,
            block_id=block_id,
            tipo=tipo,
            contenido_url=contenido_url,
            contenido_texto=contenido_texto,
        )

        self.add_child(instance=elemento)

    def _actualizar_elemento_si_necesario(self, elemento, block_value):
        thumbnail = block_value.get("thumbnail")
        alt_thumbnail = block_value.get("alt_thumbnail", "")
        tipo = block_value.get("tipo", "imagen")
        contenido_url = block_value.get("contenido_url", "")
        contenido_texto = block_value.get("contenido_texto", "")

        block_tiene_thumbnail = thumbnail is not None
        elemento_tiene_thumbnail = elemento.thumbnail_id is not None

        necesita_actualizar = (
            block_tiene_thumbnail != elemento_tiene_thumbnail
            or (block_tiene_thumbnail and elemento.thumbnail_id != thumbnail.id)
        ) or (
            elemento.alt_thumbnail != alt_thumbnail
        ) or (
            elemento.titulo != block_value.get('titulo')
        ) or (
            elemento.tipo != tipo
        ) or (
            elemento.contenido_url != contenido_url
        ) or (
            elemento.contenido_texto != contenido_texto
        )

        if necesita_actualizar:
            elemento._syncing_from_block = True
            elemento.thumbnail = block_value.get('thumbnail')
            elemento.alt_thumbnail = block_value.get('alt_thumbnail')
            elemento.titulo = block_value.get('titulo')
            elemento.tipo = tipo
            elemento.contenido_url = contenido_url
            elemento.contenido_texto =  contenido_texto
            elemento.save()

    def _eliminar_elemento(self, elemento):
        elemento._state.adding = False
        elemento.delete()

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        hijos = self.get_children().specific().order_by('path')
        block_ids_en_streamfield = {
            block.value.get('block_id'): block
            for block in self.elementos
            if block.value.get('block_id')
        }

        elementos = []
        for hijo in hijos:
            # No se muestran elementos sin block_id en el streamfield
            # o con block_id_no_reconocido
            if isinstance(hijo, ElementoPage) and \
                    str(hijo.block_id) in block_ids_en_streamfield:
                elementos.append(hijo)

        context["elementos"] = elementos
        return context

    def get_producto_anterior(self) -> Self | None:
        prev = self.get_prev_sibling()
        return prev.specific if prev else None

    def get_producto_siguiente(self) -> Self | None:
        next = self.get_next_sibling()
        return next.specific if next else None


class ElementoPage(Page):
    block_id = models.UUIDField(null=True, blank=True, editable=False)
    thumbnail = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="imagen",
    )
    alt_thumbnail = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="alt imagen",
    )
    titulo = models.CharField(max_length=255, null=True, blank=True)
    descripcion = RichTextField(blank=True)
    comentarios = StreamField(
        [("comentario", wagtail.blocks.RichTextBlock())],
        blank=True,
        use_json_field=True,
    )
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        default="imagen",
    )
    contenido_url = models.URLField(blank=True)
    contenido_texto = models.TextField(blank=True)

    parent_page_types = ["produccion.ProductoPage"]

    content_panels = Page.content_panels + [
        FieldPanel("tipo"),
        MultiFieldPanel(
            [FieldPanel("thumbnail"), FieldPanel("alt_thumbnail")],
            heading="Thumbnail",
        ),
        MultiFieldPanel(
            [FieldPanel("contenido_url"), FieldPanel("contenido_texto")],
            heading="Contenido",
        ),
        FieldPanel("titulo"),
        FieldPanel("descripcion"),
        FieldPanel("comentarios"),
    ]

    @property
    def imagen(self):
        return self.thumbnail

    @imagen.setter
    def imagen(self, value):
        self.thumbnail = value

    @property
    def alt_imagen(self):
        return self.alt_thumbnail

    @alt_imagen.setter
    def alt_imagen(self, value):
        self.alt_thumbnail = value

    def get_thumbnail_url(self, width=400):
        if self.thumbnail:
            return self.thumbnail.get_rendition(f"width-{width}").url
        if self.tipo == "video" and self.contenido_url:
            try:
                embed = get_embed(self.contenido_url)
                return embed.thumbnail_url
            except EmbedException:
                pass
        return static(f"img/default_{self.tipo}.png")

    def save(self, *args, **kwargs):
        if getattr(self, '_syncing_from_block', False):
            super().save(*args, **kwargs)
            return

        bypass_sync = kwargs.pop('bypass_sync', False)

        if self.block_id and self.pk is not None and not self._state.adding and not bypass_sync:
            padre = self.get_parent()
            if padre and hasattr(padre.specific, 'elementos'):
                self._sincronizar_desde_elemento(padre.specific)

        super().save(*args, **kwargs)

    def _sincronizar_desde_elemento(self, padre):
        nuevos_blocks = []
        for block in padre.elementos:
            block_value = dict(block.value)
            if str(block_value.get('block_id')) == str(self.block_id):
                block_value['thumbnail'] = self.thumbnail
                block_value['alt_thumbnail'] = self.alt_thumbnail
                block_value['titulo'] = self.titulo
                block_value['tipo'] = self.tipo
                block_value['contenido_url'] = self.contenido_url
            nuevos_blocks.append(('elemento', block_value))

        padre.elementos = StreamValue(
            stream_block=padre._meta.get_field('elementos').stream_block,
            stream_data=nuevos_blocks,
            is_lazy=False
        )
        padre.save(update_fields=['elementos'], bypass_sync=True)
