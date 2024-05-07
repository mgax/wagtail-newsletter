from abc import ABC, abstractmethod
from typing import Optional

from django.conf import settings
from django.utils.module_loading import import_string

from .. import audiences, models


DEFAULT_CAMPAIGN_BACKEND = (
    "wagtail_newsletter.campaign_backends.mailchimp.MailchimpCampaignBackend"
)


class CampaignBackend(ABC):
    name: str

    @abstractmethod
    def get_audiences(self) -> "list[audiences.Audience]": ...

    @abstractmethod
    def get_audience_segments(
        self, audience_id
    ) -> "list[audiences.AudienceSegment]": ...

    @abstractmethod
    def save_campaign(
        self,
        *,
        campaign_id: Optional[str] = None,
        recipients: "Optional[models.NewsletterRecipientsBase]",
        subject: str,
        content: str,
    ) -> str: ...

    @abstractmethod
    def send_test_email(self, *, campaign_id: str, email_address: str): ...


def get_backend() -> CampaignBackend:
    backend_class = import_string(
        getattr(
            settings, "WAGTAIL_NEWSLETTER_CAMPAIGN_BACKEND", DEFAULT_CAMPAIGN_BACKEND
        )
    )
    return backend_class()
