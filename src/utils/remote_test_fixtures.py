import json
import re
import traceback
import uuid

from django.apps import apps
from django.core.files.base import ContentFile
from django.http import Http404, JsonResponse
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from wagtail.blocks import StreamValue
from wagtail.documents import get_document_model
from wagtail.images import get_image_model
from wagtail.models import Collection, Page, Site, ReferenceIndex

from home.models import HomePage
from paginas.models import CurriculumPage
from produccion.models import AreaPage, ElementoPage
from utils.remote_test_utils import _check_test_token


Image = get_image_model()
Document = get_document_model()

BLOCK_FIELDS = {"thumbnail", "alt_thumbnail", "tipo", "titulo", "block_id"}
SIMPLE_PAGE_TYPES = {
    "acerca_de": "paginas.AcercaDePage",
    "contacto": "paginas.ContactPage",
}
TEST_IMAGE_TITLES = {"thumbnail de test", "imagen de franja"}
TEST_DOCUMENT_TITLE_PREFIX = "documento de test "


def _crear_home():
    """ Crea homepage para tests."""
    site = (
        Site.objects.filter(is_default_site=True).first()
        or Site.objects.first()
    )
    if site is None:
        raise Http404()

    home = HomePage(title="Test Home", slug=f"test-home-{uuid.uuid4().hex[:8]}")
    site.root_page.add_child(instance=home)
    home.save_revision().publish()
    return home


def _safe_json(view):
    @csrf_exempt
    @require_POST
    def wrapper(request):
        try:
            _check_test_token(request)
            return view(request)
        except Http404:
            raise
        except Exception:
            return JsonResponse(
                {"error": "internal", "traceback": traceback.format_exc()},
                status=500,
            )
    return wrapper


def _crear_modelo_desde_field(field_name, uploaded_file):
    """ Crea un modelo Wagtail (Image o Document) a partir de un archivo subido."""
    if field_name == "thumbnail":
        content = ContentFile(uploaded_file.read(), name="test.png")
        obj = Image(title="thumbnail de test")
        obj.file.save("test.png", content, save=False)
        obj.save()
        return obj

    if field_name == "contenido_multimedia":
        Document = get_document_model()
        content = ContentFile(uploaded_file.read(), name=uploaded_file.name)
        doc = Document(
            title=f"documento de test {uploaded_file.name}",
            collection=Collection.get_first_root_node(),
        )
        doc.file.save(uploaded_file.name, content, save=False)
        doc.save()
        return doc

    return None


def _serializar(p):
    """ Serializa una página a dict para el JSON de respuesta."""
    return {
        "url": p.url,
        "pk": p.pk,
        "title": p.title,
        "titulo": p.titulo,
        "descripcion": p.descripcion,
    }


def _get_contenedor(padre_pk):
    try:
        padre = ElementoPage.objects.get(pk=padre_pk)
        if not padre.compuesto:
            return JsonResponse({"error": "El padre no es compuesto"}, status=400)
        return padre
    except ElementoPage.DoesNotExist:
        pass
    try:
        return AreaPage.objects.get(pk=padre_pk)
    except (AreaPage.DoesNotExist, ValueError):
        return JsonResponse({"error": "padre_pk inválido"}, status=400)


def _test_pages_candidatos():
    return Page.objects.filter(slug__regex=r"^test-home-[0-9a-f]{8}$")


def _prune_test_pages(model, slug_base):
    """ Limpia residuos de tests previos"""
    for previo in model.objects.filter(
            slug__regex=rf"^{re.escape(slug_base)}-[0-9a-f]{{8}}$"):
        previo.delete()


def _prune_test_pages_remnant():
    paginas = _test_pages_candidatos()
    n = paginas.count()
    for p in paginas:
        p.delete()
    return n


def _test_media_candidatos():
    imagenes = Image.objects.filter(title__in=TEST_IMAGE_TITLES)
    documentos = Document.objects.filter(
        title__startswith=TEST_DOCUMENT_TITLE_PREFIX
    )

    uso_img = ReferenceIndex.get_count_references_to_in_bulk(imagenes)
    uso_doc = ReferenceIndex.get_count_references_to_in_bulk(documentos)

    imagenes = [i for i in imagenes if uso_img.get(i, 0) == 0]
    documentos = [d for d in documentos if uso_doc.get(d, 0) == 0]
    return imagenes, documentos


def _prune_test_media():
    imagenes, documentos = _test_media_candidatos()
    for obj in imagenes + documentos:
        obj.delete()
    return len(imagenes), len(documentos)


@_safe_json
def fixtures_homepage(request):
    _check_test_token(request)

    site = Site.objects.filter(is_default_site=True).first() or Site.objects.first()
    if site is None:
        raise Http404()
    homepage = site.root_page.specific
    if not isinstance(homepage, HomePage):
        return JsonResponse({"error": "Root page no es HomePage"}, status=400)

    original_body = list(homepage.body.raw_data)

    imagen = None
    imagen_file = request.FILES.get("imagen")
    if imagen_file:
        content = ContentFile(imagen_file.read(), name="franja.png")
        imagen = Image(title="imagen de franja")
        imagen.file.save("franja.png", content, save=False)
        imagen.save()

    area_url = request.POST.get("area_url", "")
    homepage.body = StreamValue(
        homepage.body.stream_block,
        [("franja", {
            "imagen": imagen,
            "url": {"link_to": "custom_url", "custom_url": area_url}
        })],
        is_lazy=False,
    )
    homepage.save_revision().publish()

    return JsonResponse({
        "url": homepage.url,
        "pk": homepage.pk,
        "original_body": original_body,
        "imagen_pk": imagen.pk if imagen else None,
    })


@_safe_json
def fixtures_area(request):
    _check_test_token(request)
    home = _crear_home()
    area = AreaPage(
        title=f"Area test {uuid.uuid4().hex[:6]}",
        slug=f"area-test-{uuid.uuid4().hex[:8]}",
        titulo="Area Page",
        descripcion="Página de área genérica",
    )
    home.add_child(instance=area)
    area.save_revision().publish()

    return JsonResponse({
        "home": {"pk": home.pk, "url": home.url},
        "area": _serializar(area)
    })


@_safe_json
def fixtures_elemento_compuesto(request):
    _check_test_token(request)
    titulo = request.POST.get("titulo", "Elemento Compuesto")
    descripcion = request.POST.get("descripcion", "")

    padre = _get_contenedor(request.POST.get("padre_pk"))
    if isinstance(padre, JsonResponse):
        return padre

    block_id = uuid.uuid4()
    elemento = ElementoPage(
        title=f"Elemento compuesto test {uuid.uuid4().hex[:6]}",
        slug=f"elemento-compuesto-{uuid.uuid4().hex[:8]}",
        titulo=titulo,
        descripcion=descripcion,
        compuesto=True,
        block_id=block_id,
    )
    padre.add_child(instance=elemento)

    block_value = {
        "compuesto": True,
        "thumbnail": None,
        "alt_thumbnail": "",
        "tipo": "imagen",
        "titulo": titulo,
        "block_id": str(block_id),
    }
    padre.elementos += StreamValue(
        padre.elementos.stream_block,
        [("elemento", block_value)],
        is_lazy=False,
    )
    padre.save()

    return JsonResponse({"elemento": _serializar(elemento)})


@_safe_json
def fixtures_elemento(request):
    _check_test_token(request)

    padre = _get_contenedor(request.POST.get("padre_pk"))
    if isinstance(padre, JsonResponse):
        return padre

    tipo = request.POST.get("tipo", "imagen")
    titulo = request.POST.get("titulo", "Elemento")
    alt_thumbnail = request.POST.get("alt_thumbnail", "")
    compuesto = request.POST.get("compuesto", "false") == "true"

    block_value = {
        "compuesto": compuesto,
        "thumbnail": None,
        "alt_thumbnail": alt_thumbnail,
        "tipo": tipo,
        "titulo": titulo,
        "block_id": str(uuid.uuid4()),
    }

    imagenes_creadas = []
    documentos_creados = []
    for field_name, uploaded_file in request.FILES.items():
        instance = _crear_modelo_desde_field(field_name, uploaded_file)
        if instance is not None:
            block_value[field_name] = instance

            # Registrar media creada para poder eliminarla en el cleanup
            if isinstance(instance, Image):
                imagenes_creadas.append(instance.pk)
            else:
                documentos_creados.append(instance.pk)

    page_data_raw = request.POST.get("page_data")
    page_data_dict = {}
    if page_data_raw:
        page_data_dict = json.loads(page_data_raw)

    page_fields = {}
    for key, value in page_data_dict.items():
        if key in BLOCK_FIELDS:
            block_value[key] = value
        else:
            page_fields[key] = value

    padre.elementos += StreamValue(
        padre.elementos.stream_block,
        [("elemento", block_value)],
        is_lazy=False,
    )
    padre.save()

    elemento = next(
        e for e in padre.get_children().specific()
        if str(e.block_id) == block_value["block_id"]
    )

    for key, value in page_fields.items():
        if hasattr(elemento, key):
            setattr(elemento, key, value)
    elemento.save()

    return JsonResponse({
        **_serializar(elemento),
        "imagenes": imagenes_creadas,
        "documentos": documentos_creados,
    })


@_safe_json
def fixtures_pagina_simple(request):
    _check_test_token(request)

    tipo = request.POST.get("tipo")
    if tipo not in SIMPLE_PAGE_TYPES:
        return JsonResponse({"error": f"tipo no permitido: {tipo}"}, status=400)

    app_label, _, model_name = SIMPLE_PAGE_TYPES[tipo].partition(".")
    Model = apps.get_model(app_label, model_name)
    if not issubclass(Model, Page):
        return JsonResponse({"error": "modelo no es Page"}, status=400)

    site = Site.objects.filter(is_default_site=True).first() or Site.objects.first()
    if site is None:
        raise Http404()

    title = request.POST.get("title", "Página de prueba")

    slug_base = slugify(title)
    _prune_test_pages(Model, slug_base)
    slug = f"{slug_base}-{uuid.uuid4().hex[:8]}"

    pagina = Model(title=title, slug=slug)

    page_data_raw = request.POST.get("page_data")
    if page_data_raw:
        for key, value in json.loads(page_data_raw).items():
            if hasattr(pagina, key):
                setattr(pagina, key, value)

    if request.POST.get("show_in_menus") == "true":
        pagina.show_in_menus = True

    site.root_page.add_child(instance=pagina)
    pagina.save_revision().publish()

    return JsonResponse({
        "url": pagina.url,
        "pk": pagina.pk,
        "title": pagina.title,
    })


@_safe_json
def fixtures_curriculum(request):
    _check_test_token(request)

    site = Site.objects.filter(is_default_site=True).first() or Site.objects.first()


    title = request.POST.get("title", "Curriculum")
    base_slug = slugify(title)
    _prune_test_pages(CurriculumPage, base_slug)
    slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"

    pagina = CurriculumPage(title=title, slug=slug)

    if request.POST.get("show_in_menus") == "true":
        pagina.show_in_menus = True

    entradas_raw = request.POST.get("entradas")
    if entradas_raw:
        entradas = json.loads(entradas_raw)
        pagina.entradas = StreamValue(
            pagina.entradas.stream_block,
            [("entrada", e) for e in entradas],
            is_lazy=False,
        )

    site.root_page.add_child(instance=pagina)
    pagina.save_revision().publish()

    return JsonResponse({
        "url": pagina.url,
        "pk": pagina.pk,
        "title": pagina.title,
    })


@_safe_json
def fixtures_homepage_cleanup(request):
    _check_test_token(request)

    site = Site.objects.filter(is_default_site=True).first() or Site.objects.first()
    if site is None:
        return JsonResponse({"status": "ok", "restored": False})

    homepage = site.root_page.specific
    original_raw = request.POST.get("original_body")
    if original_raw:
        field = homepage._meta.get_field("body")
        homepage.body = field.stream_block.to_python(json.loads(original_raw))
        homepage.save_revision().publish()

    return JsonResponse({"status": "ok", "restored": bool(original_raw)})


@_safe_json
def fixtures_pagina_cleanup(request):
    _check_test_token(request)
    pk = request.POST.get("pk")
    if pk:
        Page.objects.filter(pk=pk).delete()
    return JsonResponse({"status": "ok", "deleted": bool(pk)})


@_safe_json
def fixtures_media_cleanup(request):
    _check_test_token(request)

    imagen_pks = json.loads(request.POST.get("imagen_pks") or "[]")
    documento_pks = json.loads(request.POST.get("documento_pks") or "[]")

    if imagen_pks:
        Image.objects.filter(pk__in=imagen_pks).delete()
    if documento_pks:
        Document.objects.filter(pk__in=documento_pks).delete()

    return JsonResponse({
        "status": "ok",
        "imagenes": len(imagen_pks),
        "documentos": len(documento_pks),
    })


@csrf_exempt
@require_POST
@_safe_json
def fixtures_producto_cleanup(request):
    _check_test_token(request)
    home_pk = request.POST.get("home_pk")
    if home_pk:
        Page.objects.filter(pk=home_pk).delete()
    return JsonResponse({"status": "ok", "deleted": bool(home_pk)})
