from __future__ import annotations

import uuid
from typing import Self

from django.db import models
from django.utils.text import slugify
import wagtail.blocks
from wagtail.admin.panels import FieldPanel, HelpPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.blocks import StreamValue

from produccion.blocks import ProduccionStreamBlock, ElementosStreamBlock


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
        imagen = block_value.get('imagen')
        alt_imagen = block_value.get('alt_imagen')
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
            imagen=imagen,
            alt_imagen=alt_imagen,
            titulo=titulo,
            block_id=block_id,
        )

        self.add_child(instance=elemento)

    def _actualizar_elemento_si_necesario(self, elemento, block_value):
        necesita_actualizar = (
            elemento.imagen_id != block_value.get('imagen') if block_value.get('imagen') else elemento.imagen_id is not None
        ) or (
            elemento.alt_imagen != block_value.get('alt_imagen')
        ) or (
            elemento.titulo != block_value.get('titulo')
        )

        if necesita_actualizar:
            elemento._syncing_from_block = True
            elemento.imagen = block_value.get('imagen')
            elemento.alt_imagen = block_value.get('alt_imagen')
            elemento.titulo = block_value.get('titulo')
            elemento.save()

    def _eliminar_elemento(self, elemento):
        elemento._state.adding = False
        elemento.delete()

    def _actualizar_elemento(self, elemento, block_value):
        elemento._syncing_from_block = True

        elemento.title = block_value.get('titulo', elemento.title)
        elemento.slug = block_value.get('titulo', elemento.title)
        if elemento.slug:
            elemento.slug = slugify(elemento.slug) or f"elemento-{uuid.uuid4().hex[:8]}"

        elemento.imagen = block_value.get('imagen')

        elemento.alt_imagen = block_value.get('alt_imagen')
        elemento.titulo = block_value.get('titulo', '')
        elemento.block_id = block_value.get('block_id')

        elemento.save()
        if hasattr(elemento, '_syncing_from_block'):
            delattr(elemento, '_syncing_from_block')

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
    imagen = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    alt_imagen = models.CharField(max_length=255, null=True, blank=True)
    titulo = models.CharField(max_length=255, null=True, blank=True)
    alto = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        verbose_name="Alto"
    )
    ancho = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        verbose_name="Ancho"
    )
    profundidad = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        verbose_name="Profundidad"
    )
    UNIDAD_CHOICES = [
        ("cm", "cm"),
        ("mm", "mm"),
        ("m", "m"),
    ]
    unidad = models.CharField(
        max_length=10, choices=UNIDAD_CHOICES, blank=True, default="cm",
        verbose_name="Unidad de medida"
    )
    peso = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        verbose_name="Peso"
    )
    UNIDAD_PESO_CHOICES = [
        ("g", "g"),
        ("kg", "kg"),
    ]
    unidad_peso = models.CharField(
        max_length=10, choices=UNIDAD_PESO_CHOICES, blank=True, default="kg",
        verbose_name="Unidad de peso"
    )
    descripcion = RichTextField(blank=True)
    comentarios = StreamField(
        [("comentario", wagtail.blocks.RichTextBlock())],
        blank=True,
        use_json_field=True,
    )

    parent_page_types = ["produccion.ProductoPage"]

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [FieldPanel("imagen"), FieldPanel("alt_imagen")],
            heading="Imagen",
        ),
        FieldPanel("titulo"),
        MultiFieldPanel(
            [
                FieldPanel("alto"),
                FieldPanel("ancho"),
                FieldPanel("profundidad"),
                FieldPanel("unidad"),
            ],
            heading="Dimensiones",
        ),
        MultiFieldPanel(
            [
                FieldPanel("peso"),
                FieldPanel("unidad_peso"),
            ],
            heading="Peso",
        ),
        FieldPanel("descripcion"),
        FieldPanel("comentarios"),
    ]

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
                block_value['imagen'] = self.imagen
                block_value['alt_imagen'] = self.alt_imagen
                block_value['titulo'] = self.titulo
            nuevos_blocks.append(('elemento', block_value))

        padre.elementos = StreamValue(
            stream_block=padre._meta.get_field('elementos').stream_block,
            stream_data=nuevos_blocks,
            is_lazy=False
        )
        padre.save(update_fields=['elementos'], bypass_sync=True)
