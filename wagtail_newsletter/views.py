from typing import cast

from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from wagtail.models import Page

from . import campaign_backends
from .models import NewsletterPageMixin


# TODO DRF
def save_campaign(request: HttpRequest, page_id):
    page = cast(NewsletterPageMixin, get_object_or_404(Page, pk=page_id).specific)

    # TODO check editor permissions

    backend = campaign_backends.get_backend()
    revision = cast(NewsletterPageMixin, page.get_latest_revision_as_object())
    page.newsletter_campaign = backend.save_campaign(
        campaign_id=page.newsletter_campaign,
        recipients=revision.newsletter_recipients,
        subject=revision.newsletter_subject or revision.title,
        content=revision.get_newsletter_html(),
    )
    page.save(update_fields=["newsletter_campaign"])

    return JsonResponse(
        {
            "message": "Draft saved",
            "state": {
                "campaign_id": page.newsletter_campaign,
            },
        }
    )
