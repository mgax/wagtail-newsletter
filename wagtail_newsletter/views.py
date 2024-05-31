import json

from typing import Optional, cast

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from wagtail.admin import messages
from wagtail.models import ContentType, Page, Revision

from . import campaign_backends, panels
from .models import NewsletterPageMixin


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


def get_campaign(request: HttpRequest, page_id: int):
    page = cast(NewsletterPageMixin, get_object_or_404(Page, pk=page_id).specific)
    backend = campaign_backends.get_backend()
    if page.newsletter_campaign:
        campaign = backend.get_campaign(campaign_id=page.newsletter_campaign)
    else:
        campaign = None
    return _render_panel(request, page, campaign)


def save_campaign(request: HttpRequest, page_id: int, revision_id: int):
    edit_url = reverse("wagtailadmin_pages:edit", kwargs={"page_id": page_id})
    next_url = f"{edit_url}#tab-newsletter"

    page = cast(NewsletterPageMixin, get_object_or_404(Page, pk=page_id).specific)
    revision = cast(
        NewsletterPageMixin,
        get_object_or_404(
            Revision,
            base_content_type=ContentType.objects.get_for_model(Page),
            pk=revision_id,
        ).as_object(),
    )
    subject = revision.newsletter_subject or revision.title
    newsletter_data = {
        "recipients": revision.newsletter_recipients,
        "subject": subject,
        "html": revision.get_newsletter_html(),
    }

    backend = campaign_backends.get_backend()

    if request.method == "POST":
        page.newsletter_campaign = backend.save_campaign(
            campaign_id=page.newsletter_campaign,
            **newsletter_data,
        )
        page.save(update_fields=["newsletter_campaign"])

        campaign = backend.get_campaign(campaign_id=page.newsletter_campaign)
        messages.success(
            request,
            f'Campaign "{subject}" saved successfully.',
            buttons=[
                messages.button(campaign.url, f"View in {backend.name}"),
            ],
        )
        return redirect(next_url)

    context = {
        "page": page,
        "revision_id": revision.pk,
        "newsletter": newsletter_data,
        "backend_name": backend.name,
        "next_url": next_url,
    }
    return render(request, "wagtail_newsletter/save_campaign.html", context)


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
