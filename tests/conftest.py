from __future__ import annotations

import os
import uuid

import pytest
from django.conf import settings
from django.contrib.auth.models import User
from wagtail.blocks import StreamValue
from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Collection, Locale, Page, Site

from home.models import HomePage
from produccion.models import AreaPage, ElementoPage, ProductoPage
from utils.test_utils import get_elemento_por_block_id


def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker(pytest.mark.django_db(transaction=True))


@pytest.fixture(scope="session")
def live_server_url(live_server):
    if test_server := os.environ.get("TEST_SERVER"):
        return "http://" + test_server
    return live_server.url


@pytest.fixture(autouse=True)
def locale():
    # Locale. Necesario para poder crear páginas
    Locale.objects.get_or_create(language_code=settings.LANGUAGE_CODE)


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
    parts = live_server_url.replace("http://", "").split(":")
    return int(parts[1]) if len(parts) > 1 else 80


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
def elemento_factory(db, site):
    def _factory(producto, imagen=None, alt_imagen="Imagen", titulo="Elemento", page_data=None):
        block_id = uuid.uuid4()
        stream_data = [
            ("elemento", {
                "imagen": imagen,
                "alt_imagen": alt_imagen,
                "titulo": titulo,
                "block_id": block_id,
            }),
        ]
        producto.elementos += StreamValue(
            producto.elementos.stream_block,
            stream_data,
            is_lazy=False,
        )
        producto.save()

        page = get_elemento_por_block_id(producto, block_id)

        if page_data:
            print("PAGE DATA:", page_data)
            for key, value in page_data.items():
                print(f"{key}: {value}")
                if key != "imagen":
                    setattr(page, key, value)
            page.save()

        return page

    return _factory


@pytest.fixture
def area_page(test_page):
    return test_page(
        page_type=AreaPage,
        title="AreaPage",
        titulo="Area Page",
        descripcion="Página de área genérica",
        show_in_menus=True,
    )


@pytest.fixture
def producto_page(test_page, area_page):
    return test_page(
        parent=area_page,
        page_type=ProductoPage,
        title="ProductoPage",
        titulo="Producto Page",
        descripcion="Página de producto genérica",
    )


@pytest.fixture
def elemento(elemento_factory, objeto_imagen, producto_page):
    return elemento_factory(
        producto=producto_page,
        imagen=objeto_imagen,
        alt_imagen="Imagen de elemento",
        titulo="Elemento"
    )


@pytest.fixture
def elemento_2(elemento_factory, objeto_imagen, producto_page):
    return elemento_factory(
        producto=producto_page,
        imagen=objeto_imagen,
        alt_imagen="Imagen de segundo elemento",
        titulo="Segundo elemento"
    )


@pytest.fixture
def elemento_3(elemento_factory, producto_page, objeto_imagen):
    return elemento_factory(
        producto=producto_page,
        imagen=objeto_imagen,
        alt_imagen="Imagen de tercer elemento",
        titulo="Tercer elemento"
    )


@pytest.fixture
def objeto_imagen(root_collection):
    Image = get_image_model()
    image = Image(title="imagen de prueba")
    image.file = get_test_image_file()
    image.save()
    return image


@pytest.fixture
def root_collection():
    # Colección raíz: necesaria para guardar imágenes de Wagtail
    if not Collection.objects.filter(depth=1).exists():
        Collection.add_root(name="Root")
