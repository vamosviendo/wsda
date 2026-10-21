from django.urls import path

from utils.remote_test_fixtures import (
    fixtures_area,
    fixtures_curriculum,
    fixtures_elemento,
    fixtures_elemento_compuesto,
    fixtures_homepage,
    fixtures_homepage_cleanup,
    fixtures_pagina_cleanup,
    fixtures_pagina_simple,
    fixtures_media_cleanup,
)
from utils.remote_test_utils import (
    delete_document_smoke,
    deployment_smoke,
    deployment_smoke_cleanup,
    remote_test_admin,
)

urlpatterns = [
    path("admin-user/", remote_test_admin, name="remote-test-admin"),
    path("deployment-smoke/", deployment_smoke, name="deployment-smoke"),
    path("deployment-smoke/cleanup/", deployment_smoke_cleanup, name="deployment-smoke-cleanup"),
    path("delete-document/", delete_document_smoke, name="delete-document-smoke"),
    path("fixtures/homepage/", fixtures_homepage, name="fixtures-homepage"),
    path("fixtures/homepage/cleanup/", fixtures_homepage_cleanup, name="fixtures-homepage-cleanup"),
    path("fixtures/area/", fixtures_area, name="fixture-area"),
    path("fixtures/elemento/", fixtures_elemento, name="fixture-elemento"),
    path("fixtures/elemento/compuesto/", fixtures_elemento_compuesto, name="fixtures-elemento-compuesto"),
    path("fixtures/media/cleanup/", fixtures_media_cleanup, name="fixtures-media-cleanup"),
    path("fixtures/pagina/", fixtures_pagina_simple, name="fixtures-pagina"),
    path("fixtures/curriculum/", fixtures_curriculum, name="fixtures-curriculum"),
    path("fixtures/pagina/cleanup/", fixtures_pagina_cleanup, name="fixtures-pagina-cleanup"),
]
