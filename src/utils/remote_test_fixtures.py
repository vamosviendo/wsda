import json
import traceback
import uuid

from django.core.files.base import ContentFile
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from wagtail.blocks import StreamValue
from wagtail.documents import get_document_model
from wagtail.images import get_image_model
from wagtail.models import Collection, Page, Site

from home.models import HomePage
from produccion.models import AreaPage, ElementoPage, ProductoPage
from utils.remote_test_utils import _check_test_token


Image = get_image_model()


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


@_safe_json
def fixtures_producto(request):
    _check_test_token(request)
    titulo = request.POST.get("titulo", "Producto Page")
    descripcion = request.POST.get("descripcion", "")

    home = _crear_home()

    area = AreaPage(
        title=f"Area test {uuid.uuid4().hex[:6]}",
        slug=f"area-test-{uuid.uuid4().hex[:8]}",
        titulo="Area Page",
        descripcion="Página de area de test",
    )
    home.add_child(instance=area)
    area.save_revision().publish()

    producto = ProductoPage(
        title=f"Producto test {uuid.uuid4().hex[:6]}",
        slug=f"producto-test-{uuid.uuid4().hex[:8]}",
        titulo=titulo,
        descripcion=descripcion,
    )
    area.add_child(instance=producto)
    producto.save_revision().publish()

    def _ser(p):
        return {
            "url": p.url, "pk": p.pk, "title": p.title,
            "titulo": p.titulo, "descripcion": p.descripcion
        }

    return JsonResponse({
        "home": {"pk": home.pk, "url": home.url},
        "area": _ser(area),
        "producto": _ser(producto),
    })


@_safe_json
def fixtures_producto_elemento(request):
    _check_test_token(request)

    try:
        producto = ProductoPage.objects.get(pk=request.POST.get("producto_pk"))
    except (ProductoPage.DoesNotExist, ValueError):
        return JsonResponse({"error": "Producto_pk inválido"}, status=400)

    tipo = request.POST.get("tipo", "imagen")
    titulo = request.POST.get("titulo", "Elemento")
    alt_thumbnail = request.POST.get("alt_thumbnail", "")

    block_value = {
        "thumbnail": None,
        "alt_thumbnail": alt_thumbnail,
        "tipo": tipo,
        "titulo": titulo,
        "block_id": str(uuid.uuid4())
    }

    for field_name, uploaded_file in request.FILES.items():
        instance = _crear_modelo_desde_field(field_name, uploaded_file)
        if instance is not None:
            block_value[field_name] = instance

    page_data_raw = request.POST.get("page_data")
    if page_data_raw:
        block_value.update(json.loads(page_data_raw))

    producto.elementos += StreamValue(
        producto.elementos.stream_block,
        [("elemento", block_value)],
        is_lazy=False,
    )
    producto.save()

    elemento = next(
        e for e in producto.get_children().specific()
        if str(e.block_id) == block_value["block_id"]
    )
    return JsonResponse({
        "url": elemento.url,
        "pk": elemento.pk,
        "title": elemento.title,
        "tipo": elemento.tipo,
        "block_id": block_value["block_id"],
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
