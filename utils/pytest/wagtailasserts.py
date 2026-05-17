import pytest
from django.urls import reverse
from django.utils.text import slugify
from wagtail.models import Page


def assert_can_create_at(parent_model, child_model):
    """Versión py8test de WagtailTestCase.assertCanCreateAt"""
    assert child_model in parent_model.allowed_subpage_models()


def assert_can_create(parent_page, child_model, data, client, publish=True):
    """Versión pytest de WagtailGestCase.assertCanCreate"""
    # 1. Verificar relación permitida
    assert_can_create_at(parent_page.specific_class, child_model)
    # assert_can_create_at(type(parent_page), child_model)

    # 2. Preparar datos
    if "slug" not in data and "title" in data:
        data["slug"] = slugify(data["title"])
    if publish:
        data["action-publish"] = "action-publish"

    # 3. Construir URL
    add_url = reverse(
        "wagtailadmin_pages:add",
        args=[
            child_model._meta.app_label,
            child_model._meta.model_name,
            parent_page.pk
        ],
    )

    # 4. Hacer POST
    response = client.post(add_url, data, follow=True)

    # 5. Verificaciones
    assert response.status_code == 200

    if response.redirect_chain == []:
        assert "form" in response.context
        form = response.context["form"]
        # Si hay errores, fallar con mensaje descriptivo
        if form.errors:
            errors = "\n".join(
                f"  {field}:\n    {', '.join(err_list)}"
                for field, err_list in sorted(form.errors.items())
            )
            pytest.fail(
                f"Validation errors found "
                f"when creating a {child_model._meta.app_label}."
                f"{child_model._meta.model_name}:"
                f"\n{errors}"
            )
        else:
            pytest.fail("Creating a page failed for an unknown reason")

    # 6. Verificar redirección
    if publish:
        expected_url = reverse("wagtailadmin_explore", args=[parent_page.pk])
    else:
        expected_url = reverse(
            "wagtailadmin_pages:edit",
            args=[Page.objects.order_by("pk").last().pk]
        )

    assert \
        response.redirect_chain == [(expected_url, 302)], \
        f"Redirect chain recibida: {response.redirect_chain}.\n" \
        f"Debe ser [({expected_url}, 302)]."
