from abc import ABC, abstractmethod

from django.conf import settings
from django.utils.module_loading import import_string

from .. import audiences


DEFAULT_CAMPAIGN_BACKEND = (
    "wagtail_newsletter.campaign_backends.mailchimp.MailchimpCampaignBackend"
)


class CampaignBackend(ABC):
    @abstractmethod
    def get_audiences(self) -> "list[audiences.Audience]":
        raise NotImplementedError

    @abstractmethod
    def get_audience_segments(self, audience_id) -> "list[audiences.AudienceSegment]":
        raise NotImplementedError


def get_backend() -> CampaignBackend:
    backend_class = import_string(
        getattr(
            settings, "WAGTAIL_NEWSLETTER_CAMPAIGN_BACKEND", DEFAULT_CAMPAIGN_BACKEND
        )
    )
    return backend_class()
