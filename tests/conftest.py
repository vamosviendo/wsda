from __future__ import annotations

import os
import uuid
from types import SimpleNamespace
from urllib.parse import urlparse

import pytest
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from wagtail.blocks import StreamValue
from wagtail.documents import get_document_model
from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Collection, Locale, Page, Site

from home.models import HomePage
from produccion.models import AreaPage, ElementoPage
from tests.remote_fixtures import RemoteProductoFixtures
from utils.test_utils import get_elemento_page_from_block_id


# Bytes mínimos válidos como placeholders de mp4 y mp3
CONTENIDO_VIDEO = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom"
CONTENIDO_AUDIO = b"\xff\xfb\x90\x00" + b"\x00" * 100


Image = get_image_model()


def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker(pytest.mark.django_db(transaction=True))


@pytest.fixture
def remote_fixtures(live_server_url):
    if not os.environ.get("TEST_SERVER"):
        yield None
        return
    token = os.environ.get("DJANGO_TEST_TOKEN")
    assert token, "TEST_SERVER definido pero falta DJANGO_TEST_TOKEN"
    client = RemoteProductoFixtures(live_server_url, token)
    yield client
    client.cleanup()


@pytest.fixture(scope="session")
def live_server_url(live_server):
    if test_server := os.environ.get("TEST_SERVER"):
        if test_server.startswith(("http://", "https://")):
            return test_server.rstrip("/")
        return f"https://{test_server}".rstrip("/")
    return live_server.url


@pytest.fixture(autouse=True)
def locale():
    # Locale. Necesario para poder crear páginas
    Locale.objects.get_or_create(language_code=settings.LANGUAGE_CODE)


@pytest.fixture(autouse=True)
def temporary_media_root(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path / "media"


@pytest.fixture
def root_page():
    # Página raíz del árbol de Wagtail. Tomar o crear
    root_page = Page.objects.filter(depth=1).first() \
             or Page.add_root(title="Root", slug="root")

    # Si quedaron hijos de un setup anterior, los borramos.
    for child in root_page.get_children():
        child.delete()
    root_page.refresh_from_db()
    return root_page


@pytest.fixture
def homepage(root_page):
    hp = HomePage(title="Home", slug="home")
    root_page.add_child(instance=hp)
    return hp


@pytest.fixture
def site_name():
    return "Rogelio Roldán"


@pytest.fixture
def hostname(live_server_url):
    return live_server_url.replace("http://", "").split(":")[0]


@pytest.fixture
def port(live_server_url):
    parsed = urlparse(live_server_url)
    return parsed.port or (443 if parsed.scheme == "https" else 80)


@pytest.fixture
def site(hostname, port, homepage, site_name):
    return Site.objects.create(
        hostname=hostname,
        port=port,
        root_page=homepage,
        is_default_site=True,
        site_name=site_name,
    )


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username="admin",
        password="adminpassword",
        email="admin@test.com",
    )


@pytest.fixture
def authenticated_client(client, admin_user):
    client.force_login(admin_user)
    return client


@pytest.fixture
def test_page(db, site):
    """A flexible fixture to create a test Wagtail page.

    Usage: `test_page(parent=some_page, page_type=MyCustomPage, title='Test Child')`
    """

    def _page_factory(parent=None, page_type=Page, title="Test Page", publish=True, **kwargs):
        # Si no se especifica parent usar página raíz por defecto del sitio
        parent = parent or site.root_page

        # Asegurar que el parent está publicado antes de agregar hijos si es necesario
        if not parent.live:
            parent.save_revision().publish()

        # Crear una instancia del tipo de página especificado:
        page_instance = page_type(title=title, **kwargs)
        parent.add_child(instance=page_instance)
        if publish:
            page_instance.save_revision().publish()

        print(f"\nCreated test page: {title} (ID: {page_instance.pk})")
        return page_instance

    yield _page_factory

    # La limpieza es manejada por el fixture db de pytest-django
    print("\nTest page cleanup (handled by transaction rollback)")


@pytest.fixture
def elemento_factory(remote_fixtures, site):
    def _factory(
            padre: AreaPage | ElementoPage, thumbnail=None, alt_thumbnail="Imagen",
            tipo="imagen", titulo="Elemento", compuesto=False, page_data=None
    ):
        if os.environ.get("TEST_SERVER"):
            return remote_fixtures.crear_elemento(
                padre.pk, tipo, titulo, alt_thumbnail,
                compuesto=compuesto,
                page_data=page_data,
                thumbnail=thumbnail,
            )

        block_id = uuid.uuid4()
        stream_data = [
            ("elemento", {
                "compuesto": compuesto,
                "thumbnail": thumbnail,
                "alt_thumbnail": alt_thumbnail,
                "tipo": tipo,
                "titulo": titulo,
                "block_id": str(block_id),
            }),
        ]
        padre.elementos += StreamValue(
            padre.elementos.stream_block,
            stream_data,
            is_lazy=False,
        )
        padre.save()

        page = get_elemento_page_from_block_id(padre, block_id)

        if page_data:
            for key, value in page_data.items():
                if key != "thumbnail":
                    setattr(page, key, value)
            page.save()

        return page

    return _factory


@pytest.fixture
def area_page(remote_fixtures, test_page):
    if os.environ.get("TEST_SERVER"):
        return remote_fixtures.setup_area()
    return test_page(
        page_type=AreaPage,
        title="AreaPage",
        titulo="Area Page",
        descripcion="Página de área genérica",
        show_in_menus=True,
    )


@pytest.fixture
def elemento_compuesto(remote_fixtures, area_page, elemento_factory):
    if os.environ.get("TEST_SERVER"):
        return remote_fixtures.setup_elemento_compuesto(
            area_page.pk, "Elemento compuesto", "Elemento compuesto genérico"
        )
    return elemento_factory(
        padre=area_page,
        compuesto=True,
        titulo="Elemento compuesto",
    )


@pytest.fixture
def elemento_compuesto_2(remote_fixtures, area_page, elemento_factory):
    if os.environ.get("TEST_SERVER"):
        return remote_fixtures.setup_elemento_compuesto(
            area_page.pk, "Elemento compuesto 2", "Segundo elemento compuesto genérico"
        )
    return elemento_factory(
        padre=area_page,
        compuesto=True,
        titulo="Elemento compuesto 2",
    )


@pytest.fixture
def elemento(elemento_factory, objeto_imagen, elemento_compuesto):
    return elemento_factory(
        padre=elemento_compuesto,
        thumbnail=objeto_imagen,
        alt_thumbnail="Imagen de elemento",
        titulo="Elemento"
    )


@pytest.fixture
def elemento_2(elemento_factory, objeto_imagen, elemento_compuesto):
    return elemento_factory(
        padre=elemento_compuesto,
        thumbnail=objeto_imagen,
        alt_thumbnail="Imagen de segundo elemento",
        titulo="Segundo elemento"
    )


@pytest.fixture
def elemento_3(elemento_factory, elemento_compuesto, objeto_imagen):
    return elemento_factory(
        padre=elemento_compuesto,
        thumbnail=objeto_imagen,
        alt_thumbnail="Imagen de tercer elemento",
        titulo="Tercer elemento"
    )


@pytest.fixture
def elemento_de_area(elemento_factory, objeto_imagen, area_page):
    return elemento_factory(
        padre=area_page,
        thumbnail=objeto_imagen,
        alt_thumbnail="Imagen de elemento de área",
        titulo="Elemento de área"
    )


@pytest.fixture
def elemento_audio(elemento_factory, elemento_compuesto):
    return elemento_factory(
        padre=elemento_compuesto,
        tipo="audio",
        titulo="Elemento de audio",
        page_data={"contenido_url": "https://soundcloud.com/test"},
    )


@pytest.fixture
def elemento_video(elemento_factory, elemento_compuesto):
    return elemento_factory(
        padre=elemento_compuesto,
        tipo="video",
        titulo="Elemento de video",
        page_data={"contenido_url": "https://www.youtube.com/watch?v=abc"},
    )


@pytest.fixture
def elemento_texto(elemento_factory, elemento_compuesto):
    return elemento_factory(
        padre=elemento_compuesto,
        tipo="texto",
        titulo="Elemento de texto",
        page_data={"contenido_texto": "<p>Texto original</p>"},
    )


@pytest.fixture
def objeto_imagen(root_collection, tmp_path):
    if os.environ.get("TEST_SERVER"):
        img_file = get_test_image_file()
        img_file.seek(0)
        content = img_file.read()
        p = tmp_path / "test.png"
        p.write_bytes(content)
        return SimpleNamespace(path=str(p))

    image = Image(title="imagen de prueba")
    image.file = get_test_image_file()
    image.save()
    return image


@pytest.fixture
def root_collection():
    # Colección raíz: necesaria para guardar imágenes de Wagtail
    if not Collection.objects.filter(depth=1).exists():
        Collection.add_root(name="Root")
    return Collection.objects.filter(depth=1).first()


@pytest.fixture
def objeto_documento_video(root_collection, tmp_path):
    """ Documento de video de prueba (mp4)."""
    contenido = CONTENIDO_VIDEO

    if os.environ.get("TEST_SERVER"):
        p = tmp_path / "video_prueba.mp4"
        p.write_bytes(contenido)
        return SimpleNamespace(path=str(p))

    Document = get_document_model()

    doc = Document(
        title="documento de video de prueba",
        collection=root_collection,
    )
    doc.file.save("video_prueba.mp4", ContentFile(contenido), save=True)
    return doc


@pytest.fixture
def objeto_documento_audio(root_collection, tmp_path):
    """ Documento de audio de prueba (mp3)."""
    # Bytes mínimos válidos como placeholder de mp3.
    contenido = CONTENIDO_AUDIO

    if os.environ.get("TEST_SERVER"):
        p = tmp_path / "audio_prueba.mp3"
        p.write_bytes(contenido)
        return SimpleNamespace(path=str(p))
    Document = get_document_model()

    doc = Document(
        title="documento de audio de prueba",
        collection=root_collection
    )
    doc.file.save("audio_prueba.mp3", ContentFile(contenido), save=True)
    return doc
