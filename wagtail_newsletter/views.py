from typing import cast

from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from wagtail.admin import messages
from wagtail.models import ContentType, Page, Revision

from . import campaign_backends
from .models import NewsletterPageMixin


# TODO DRF class-based views
# TODO check editor permissions


def save_campaign(request: HttpRequest, page_id: int, revision_id: int):
    edit_url = reverse("wagtailadmin_pages:edit", kwargs={"page_id": page_id})
    next_url = f"{edit_url}#tab-newsletter"

    # TODO redirect to next_url if campaign has been sent

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

        action = request.POST.get("action")

        if action == "send_test_email":
            recipient = request.POST["test_email_recipient"]  # TODO DRF serializer?
            backend.send_test_email(
                campaign_id=page.newsletter_campaign,
                email_address=recipient,
            )
            messages.success(request, f"Test message sent to {recipient}")

        elif action == "send_campaign":
            backend.send_campaign(page.newsletter_campaign)
            return redirect(next_url)

        return redirect(".")

    context = {
        "page": page,
        "newsletter": newsletter_data,
        "backend_name": backend.name,
        "next_url": next_url,
        "user_email": request.user.email,  # type: ignore
        "recipients": page.newsletter_recipients,
    }
    return render(request, "wagtail_newsletter/save_campaign.html", context)
