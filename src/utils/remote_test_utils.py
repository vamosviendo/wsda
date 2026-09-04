import os
import uuid

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import Http404, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from wagtail.documents import get_document_model


def _check_test_token(request):
    expected_token = os.environ.get("DJANGO_TEST_TOKEN")

    if not expected_token:
        raise Http404()

    received_token = request.headers.get("X-Test-Token")

    if received_token != expected_token:
        raise Http404()


@csrf_exempt
@require_POST
def deployment_smoke(request):
    _check_test_token(request)

    smoke_id = uuid.uuid4().hex
    session_key = f"smoke{smoke_id}"[:32]
    expected_media_content = f"staging smoke ok {smoke_id}"
    media_path = f"smoke-tests/deployment-smoke-{smoke_id}.txt"

    Session.objects.create(
        session_key=session_key,
        session_data="smoke-test",
        expire_date=timezone.now() + timezone.timedelta(minutes=5),
    )
    Session.objects.get(session_key=session_key)

    default_storage.save(
        media_path,
        ContentFile(expected_media_content.encode("utf-8")),
    )

    with default_storage.open(media_path, "rb") as media_file:
        actual_media_content = media_file.read().decode("utf-8")

    if actual_media_content != expected_media_content:
        return JsonResponse(
            {
                "database_write": "ok",
                "database_read": "ok",
                "media_write": "ok",
                "media_read": "failed",
            },
            status=500,
        )

    Session.objects.filter(session_key=session_key).delete()

    return JsonResponse(
        {
            "database_write": "ok",
            "database_read": "ok",
            "media_write": "ok",
            "media_read": "ok",
            "media_url": default_storage.url(media_path),
            "expected_media_content": expected_media_content,
        }
    )


@csrf_exempt
@require_http_methods(["POST", "DELETE"])
def remote_test_admin(request):
    _check_test_token(request)

    username = os.environ.get("DJANGO_TEST_ADMIN_USERNAME", "admin")
    password = os.environ.get("DJANGO_TEST_ADMIN_PASSWORD", "adminpassword")
    email = os.environ.get("DJANGO_TEST_ADMIN_EMAIL", "admin@test.com")

    User = get_user_model()

    if request.method == "POST":
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_active": True,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        user.set_password(password)
        user.save()

        return JsonResponse(
            {
                "status": "ok",
                "created": created,
                "username": username,
            }
        )

    User.objects.filter(username=username).delete()

    return JsonResponse(
        {
            "status": "ok",
            "deleted": True,
            "username": username,
        }
    )

@csrf_exempt
@require_POST
def delete_document_smoke(request):
    """ Elimina un documento por id. Endpoint de testing. """
    _check_test_token(request)

    document_id = request.POST.get("document_id")
    if not document_id:
        return JsonResponse({"error": "Falta document_id"}, status=400)

    Document = get_document_model()
    try:
        document = Document.objects.get(pk=document_id)
        document.delete()
        return JsonResponse({"deleted": True, "document_id": document_id})
    except Document.DoesNotExist:
        return JsonResponse(
            {"deleted": False, "error": "Documento no encontrado"},
            status=404,
        )
