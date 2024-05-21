from contextlib import contextmanager
from datetime import datetime
from typing import Any, Optional, cast

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError

from ..audiences import (
    Audience,
    AudienceSegment,
)
from ..models import NewsletterRecipientsBase
from . import Campaign, CampaignBackend


CAMPAIGN_STATUS_DRAFT = "save"


@contextmanager
def log_api_errors():
    try:
        yield
    except ApiClientError as error:
        print(error.text)
        raise


class MailchimpCampaign(Campaign):
    def __init__(
        self,
        backend: "MailchimpCampaignBackend",
        id: str,
        web_id: str,
        status: str,
    ):
        self.backend = backend
        self.id = id
        self.web_id = web_id
        self.status = status

    @property
    def sent(self):  # type: ignore
        return self.status != CAMPAIGN_STATUS_DRAFT

    @property
    def url(self):  # type: ignore
        server = self.backend.client.api_client.server
        base_url = f"https://{server}.admin.mailchimp.com"

        if self.sent:
            return f"{base_url}/reports/summary?id={self.web_id}"

        else:
            return f"{base_url}/campaigns/edit?id={self.web_id}"

    def get_report(self) -> "dict[str, Any]":
        # TODO "send_time": datetime.fromisoformat(report["send_time"]), ValueError: Invalid isoformat string: ''
        report = self.backend.client.reports.get_campaign_report(self.id)
        return {
            "send_time": datetime.fromisoformat(report["send_time"]),
            "emails_sent": report["emails_sent"],
        }


class MailchimpCampaignBackend(CampaignBackend):
    name = "Mailchimp"

    def __init__(self):
        self.client = Client()
        self.client.set_config(self.get_client_config())

    def get_client_config(self) -> "dict[str, Any]":
        if not settings.WAGTAIL_NEWSLETTER_MAILCHIMP_API_KEY:
            raise ImproperlyConfigured(
                "WAGTAIL_NEWSLETTER_MAILCHIMP_API_KEY is not set"
            )

        return {
            "api_key": settings.WAGTAIL_NEWSLETTER_MAILCHIMP_API_KEY,
            "timeout": 30,
        }

    def get_audiences(self) -> "list[Audience]":
        audiences = self.client.lists.get_all_lists()["lists"]
        return [
            Audience(
                id=audience["id"],
                name=audience["name"],
                member_count=audience["stats"]["member_count"],
            )
            for audience in audiences
        ]

    def get_audience_segments(self, audience_id) -> "list[AudienceSegment]":
        try:
            segments = self.client.lists.list_segments(audience_id)["segments"]

        except ApiClientError as error:
            if error.status_code == 404:
                raise Audience.DoesNotExist from error

            raise

        return [
            AudienceSegment(
                # Include the audience ID in the segment ID, so we can find the segment
                # later.
                id=f"{audience_id}/{segment['id']}",
                name=segment["name"],
                member_count=segment["member_count"],
            )
            for segment in segments
        ]

    def save_campaign(
        self,
        *,
        campaign_id: Optional[str] = None,
        recipients: Optional[NewsletterRecipientsBase],
        subject: str,
        content: str,
    ) -> str:
        body: dict[str, Any] = {
            "settings": {
                # TODO check that these settings are set
                "from_name": settings.WAGTAIL_NEWSLETTER_FROM_NAME,
                "reply_to": settings.WAGTAIL_NEWSLETTER_REPLY_TO,
                "subject_line": subject,
            },
        }

        if recipients is not None:
            body["recipients"] = {
                "list_id": recipients.audience,
            }

            if recipients.segment:
                segment_id = int(recipients.segment.split("/")[1])
                body["recipients"]["segment_opts"] = {
                    "saved_segment_id": segment_id,
                }

        with log_api_errors():
            if not campaign_id:
                body["type"] = "regular"
                campaign_id = cast(str, self.client.campaigns.create(body)["id"])

            else:
                self.client.campaigns.update(campaign_id, body)

            self.client.campaigns.set_content(campaign_id, {"html": content})

        return campaign_id

    def get_campaign(self, campaign_id: str):
        with log_api_errors():
            data = self.client.campaigns.get(campaign_id)

        return MailchimpCampaign(
            backend=self,
            id=campaign_id,
            web_id=data["web_id"],
            status=data["status"],
        )

    def send_test_email(self, *, campaign_id: str, email_address: str):
        with log_api_errors():
            self.client.campaigns.send_test_email(
                campaign_id,
                {
                    "test_emails": [email_address],
                    "send_type": "html",
                },
            )

    def send_campaign(self, campaign_id: str):
        with log_api_errors():
            self.client.campaigns.send(campaign_id)
