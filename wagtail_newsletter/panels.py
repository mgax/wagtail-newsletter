from wagtail.admin.panels import Panel

from . import campaign_backends, models


class NewsletterPanel(Panel):
    clean_name = "newsletter_panel"  # type: ignore

    class BoundPanel(Panel.BoundPanel):
        template_name = "wagtail_newsletter/panels/newsletter_panel.html"

        instance: "models.NewsletterPageMixin"

        class Media:
            css = {
                "all": [
                    "wagtail_newsletter/css/wagtail_newsletter.css",
                ]
            }

        def get_context_data(self, parent_context=None):
            context = super().get_context_data(parent_context) or {}

            if self.instance.pk:
                if self.instance.newsletter_campaign:
                    backend = campaign_backends.get_backend()
                    campaign = backend.get_campaign(self.instance.newsletter_campaign)

                else:
                    campaign = None

                context["campaign"] = campaign
                context["campaign_sent"] = campaign and campaign.sent

                if campaign and campaign.sent:
                    context["campaign_report"] = campaign.get_report()

            return context
