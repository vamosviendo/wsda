import os

from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.views.static import serve
from django.urls import re_path


from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("search/", search_views.search, name="search"),
]


# Para tests remotos
if os.environ.get("DJANGO_TEST_TOKEN"):
    from utils.remote_test_fixtures import (
        fixtures_area,
        fixtures_area_productos,
        fixtures_producto,
        fixtures_producto_cleanup,
        fixtures_producto_elemento,
    )
    from utils.remote_test_utils import (
        delete_document_smoke,
        deployment_smoke,
        remote_test_admin,
    )

    urlpatterns += [
        path("__test__/admin-user/", remote_test_admin, name="remote-test-admin"),
        path("__test__/deployment-smoke/", deployment_smoke, name="deployment-smoke"),
        path("__test__/delete-document/", delete_document_smoke, name="delete-document-smoke"),
        path("__test__/fixtures/area/", fixtures_area, name="fixture-area"),
        path("__test__/fixtures/area/productos/", fixtures_area_productos, name="fixture-area_productos"),
        path("__test__/fixtures/producto/", fixtures_producto, name="fixtures-producto"),
        path("__test__/fixtures/producto/elemento/", fixtures_producto_elemento, name="fixtures-producto-elemento"),
        path("__test__/fixtures/producto/cleanup/", fixtures_producto_cleanup, name="fixtures-producto-cleanup"),
    ]

# Para tests locales
if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static and media files from intranet server
# Provisorio. Se eliminará una vez que se implemente Nginx
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

urlpatterns += [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
