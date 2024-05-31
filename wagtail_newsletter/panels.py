import json

from typing import Optional

from django.urls import reverse
from wagtail.admin.panels import Panel

from . import campaign_backends, models


class NewsletterPanel(Panel):
    clean_name = "newsletter_panel"  # type: ignore

    class BoundPanel(Panel.BoundPanel):
        template_name = "wagtail_newsletter/panels/newsletter_panel.html"
        loaded = False
        campaign = None
        message = ""

        instance: "models.NewsletterPageMixin"

        class Media:
            js = [
                "wagtail_newsletter/js/wagtail_newsletter.js",
            ]
            css = {
                "all": [
                    "wagtail_newsletter/css/wagtail_newsletter.css",
                ]
            }

        def set_campaign(self, campaign: Optional[campaign_backends.Campaign]):
            self.loaded = True
            self.campaign = campaign

        def set_message(self, message: str):
            self.message = message

        def get_context_data(self, parent_context=None):
            context = super().get_context_data(parent_context) or {}
            if self.instance.pk:
                context["urls_json"] = json.dumps(
                    {
                        "getCampaign": reverse(
                            "wagtail_newsletter:get_campaign",
                            kwargs={"page_id": self.instance.pk},
                        ),
                        "sendTestEmail": reverse(
                            "wagtail_newsletter:send_test_email",
                            kwargs={"page_id": self.instance.pk},
                        ),
                        "sendCampaign": reverse(
                            "wagtail_newsletter:send_campaign",
                            kwargs={"page_id": self.instance.pk},
                        ),
                    }
                )
                context["loaded"] = self.loaded
                context["campaign"] = self.campaign
                context["campaign_sent"] = self.campaign and self.campaign.sent
                context["user_email"] = self.request.user.email
                context["recipients"] = self.instance.newsletter_recipients
                context["message"] = self.message

                if self.campaign and self.campaign.sent:
                    context["campaign_report"] = self.campaign.get_report()

            return context
