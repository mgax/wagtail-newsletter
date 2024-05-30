import json

from typing import Optional, cast

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from wagtail.models import Page

from . import campaign_backends, panels
from .models import NewsletterPageMixin, PageLockedForNewsletter


# TODO DRF class-based views
# TODO check editor permissions


def _render_panel(
    request: HttpRequest,
    page: NewsletterPageMixin,
    campaign: Optional[campaign_backends.Campaign],
    message: str = "",
):
    panel = page.get_newsletter_panel().bind_to_model(type(page))
    bound_panel = cast(
        panels.NewsletterPanel.BoundPanel,
        panel.get_bound_panel(instance=page, request=request),
    )
    bound_panel.set_campaign(campaign)
    bound_panel.set_message(message)
    return HttpResponse(bound_panel.render_html())


def _get_recipients(page, recipients_id):
    if not recipients_id:
        return None

    fields = {field.name: field for field in page._meta.fields}
    recipients_model = fields["newsletter_recipients"].related_model
    return recipients_model.objects.get(pk=recipients_id)


def _save_campaign(
    backend: campaign_backends.CampaignBackend,
    page: NewsletterPageMixin,
    body: "dict[str, str]",
):
    page.newsletter_campaign = backend.save_campaign(
        campaign_id=page.newsletter_campaign,
        recipients=_get_recipients(page, body["recipients"]),
        subject=body["subject"],
        content=body["content"],
    )
    page.save(update_fields=["newsletter_campaign"])


def get_campaign(request: HttpRequest, page_id: int):
    page = cast(NewsletterPageMixin, get_object_or_404(Page, pk=page_id).specific)
    backend = campaign_backends.get_backend()
    if page.newsletter_campaign:
        campaign = backend.get_campaign(campaign_id=page.newsletter_campaign)
    else:
        campaign = None
    return _render_panel(request, page, campaign)


def save_campaign(request: HttpRequest, page_id: int):
    page = cast(NewsletterPageMixin, get_object_or_404(Page, pk=page_id).specific)
    backend = campaign_backends.get_backend()
    _save_campaign(backend, page, json.loads(request.body))
    campaign = backend.get_campaign(campaign_id=page.newsletter_campaign)
    return _render_panel(request, page, campaign, "Campaign saved.")


def send_test_email(request: HttpRequest, page_id: int):
    page = cast(NewsletterPageMixin, get_object_or_404(Page, pk=page_id).specific)
    backend = campaign_backends.get_backend()
    backend.send_test_email(
        campaign_id=page.newsletter_campaign,
        email_address=json.loads(request.body)["email"],  # TODO DRF serializer
    )

    campaign = backend.get_campaign(campaign_id=page.newsletter_campaign)
    return _render_panel(request, page, campaign, "Test message sent.")


def send_campaign(request: HttpRequest, page_id: int):
    page = cast(NewsletterPageMixin, get_object_or_404(Page, pk=page_id).specific)
    backend = campaign_backends.get_backend()
    backend.send_campaign(page.newsletter_campaign)
    campaign = backend.get_campaign(campaign_id=page.newsletter_campaign)
    return _render_panel(request, page, campaign, "Campaign sent.")


def lock(request: HttpRequest, page_id: int):
    page = cast(NewsletterPageMixin, get_object_or_404(Page, pk=page_id).specific)
    PageLockedForNewsletter.objects.get_or_create(page=page)
    return HttpResponse()


def unlock(request: HttpRequest, page_id: int):
    page = cast(NewsletterPageMixin, get_object_or_404(Page, pk=page_id).specific)
    PageLockedForNewsletter.objects.filter(page=page).delete()
    return HttpResponse()
