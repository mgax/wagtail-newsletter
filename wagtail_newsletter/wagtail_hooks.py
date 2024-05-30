from django.urls import include, path
from django.views.i18n import JavaScriptCatalog
from wagtail import hooks

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
            "page/<int:page_id>/get_campaign",
            views.get_campaign,
            name="get_campaign",
        ),
        path(
            "page/<int:page_id>/save_campaign",
            views.save_campaign,
            name="save_campaign",
        ),
        path(
            "page/<int:page_id>/send_test_email",
            views.send_test_email,
            name="send_test_email",
        ),
        path(
            "page/<int:page_id>/send_campaign",
            views.send_campaign,
            name="send_campaign",
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
