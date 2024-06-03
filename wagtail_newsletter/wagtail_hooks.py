from django.shortcuts import redirect
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog
from wagtail import hooks
from wagtail.models import Page

from . import DEFAULT_RECIPIENTS_MODEL, get_recipients_model_string, views, viewsets


@hooks.register("register_admin_urls")  # type: ignore
def register_admin_urls():
    urls = [
        path(
            "jsi18n/",
            JavaScriptCatalog.as_view(packages=["wagtail_newsletter"]),
            name="javascript_catalog",
        ),
        path(
            "page/<int:page_id>/save_campaign/<int:revision_id>/",
            views.save_campaign,
            name="save_campaign",
        ),
    ]

    return [
        path(
            "newsletter/",
            include(
                (urls, "wagtail_newsletter"),
                namespace="wagtail_newsletter",
            ),
        )
    ]


@hooks.register("register_admin_viewset")  # type: ignore
def register_admin_viewset():
    register_viewsets = [
        viewsets.audience_chooser_viewset,
        viewsets.audience_segment_chooser_viewset,
        viewsets.recipients_chooser_viewset,
    ]
    if get_recipients_model_string() == DEFAULT_RECIPIENTS_MODEL:
        register_viewsets.append(viewsets.newsletter_recipients_viewset)
    return register_viewsets


@hooks.register("after_edit_page")  # type: ignore
def redirect_to_campaign_page(request, page: Page):
    if request.POST.get("newsletter_action"):
        revision = page.latest_revision
        if revision is None:
            raise RuntimeError(
                'A revision should have been saved by "wagtailadmin_pages:edit"'
            )
        return redirect(
            "wagtail_newsletter:save_campaign",
            page_id=page.pk,
            revision_id=revision.pk,
        )
