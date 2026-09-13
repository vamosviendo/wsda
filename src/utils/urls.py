from django.urls import path

from utils.remote_test_fixtures import (
    fixtures_area,
    fixtures_area_productos,
    fixtures_curriculum,
    fixtures_pagina_cleanup,
    fixtures_pagina_simple,
    fixtures_producto,
    fixtures_producto_cleanup,
    fixtures_producto_elemento,
)
from utils.remote_test_utils import (
    delete_document_smoke,
    deployment_smoke,
    remote_test_admin,
)

urlpatterns = [
    path("admin-user/", remote_test_admin, name="remote-test-admin"),
    path("deployment-smoke/", deployment_smoke, name="deployment-smoke"),
    path("delete-document/", delete_document_smoke, name="delete-document-smoke"),
    path("fixtures/area/", fixtures_area, name="fixture-area"),
    path("fixtures/area/productos/", fixtures_area_productos, name="fixture-area_productos"),
    path("fixtures/producto/", fixtures_producto, name="fixtures-producto"),
    path("fixtures/producto/elemento/", fixtures_producto_elemento, name="fixtures-producto-elemento"),
    path("fixtures/producto/cleanup/", fixtures_producto_cleanup, name="fixtures-producto-cleanup"),
    path("fixtures/pagina/", fixtures_pagina_simple, name="fixtures-pagina"),
    path("fixtures/curriculum/", fixtures_curriculum, name="fixtures-curriculum"),
    path("fixtures/pagina/cleanup/", fixtures_pagina_cleanup, name="fixtures-pagina-cleanup"),
]
