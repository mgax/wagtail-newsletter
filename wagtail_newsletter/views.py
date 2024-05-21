import json

from typing import Optional, cast

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from wagtail.models import Page

from . import campaign_backends, panels
from .models import NewsletterPageMixin


# TODO DRF class-based views
# TODO check editor permissions


def render_panel(
    request: HttpRequest,
    page: NewsletterPageMixin,
    campaign: Optional[campaign_backends.Campaign],
):
    panel = page.get_newsletter_panel().bind_to_model(type(page))
    bound_panel = cast(
        panels.NewsletterPanel.BoundPanel,
        panel.get_bound_panel(instance=page, request=request),
    )
    bound_panel.set_campaign(campaign)
    return HttpResponse(bound_panel.render_html())


def get_campaign(request: HttpRequest, page_id: int):
    page = cast(NewsletterPageMixin, get_object_or_404(Page, pk=page_id).specific)
    backend = campaign_backends.get_backend()
    if page.newsletter_campaign:
        campaign = backend.get_campaign(campaign_id=page.newsletter_campaign)
    else:
        campaign = None
    return render_panel(request, page, campaign)


def save_draft(request: HttpRequest, page_id: int):
    page = cast(NewsletterPageMixin, get_object_or_404(Page, pk=page_id).specific)
    backend = campaign_backends.get_backend()
    revision = cast(NewsletterPageMixin, page.get_latest_revision_as_object())
    page.newsletter_campaign = backend.save_campaign(
        campaign_id=page.newsletter_campaign,
        recipients=revision.newsletter_recipients,
        subject=revision.newsletter_subject or revision.title,
        content=revision.get_newsletter_html(),
    )
    page.save(update_fields=["newsletter_campaign"])
    campaign = backend.get_campaign(campaign_id=page.newsletter_campaign)
    return render_panel(request, page, campaign)


def send_test_email(request: HttpRequest, page_id: int):
    page = cast(NewsletterPageMixin, get_object_or_404(Page, pk=page_id).specific)
    backend = campaign_backends.get_backend()
    revision = cast(NewsletterPageMixin, page.get_latest_revision_as_object())
    page.newsletter_campaign = backend.save_campaign(
        campaign_id=page.newsletter_campaign,
        recipients=revision.newsletter_recipients,
        subject=revision.newsletter_subject or revision.title,
        content=revision.get_newsletter_html(),
    )
    page.save(update_fields=["newsletter_campaign"])

    backend.send_test_email(
        campaign_id=page.newsletter_campaign,
        email_address=json.loads(request.body)["email"],  # TODO DRF serializer
    )

    campaign = backend.get_campaign(campaign_id=page.newsletter_campaign)
    return render_panel(request, page, campaign)


def send_campaign(request: HttpRequest, page_id: int):
    page = cast(NewsletterPageMixin, get_object_or_404(Page, pk=page_id).specific)
    backend = campaign_backends.get_backend()
    backend.send_campaign(page.newsletter_campaign)
    campaign = backend.get_campaign(campaign_id=page.newsletter_campaign)
    return render_panel(request, page, campaign)
