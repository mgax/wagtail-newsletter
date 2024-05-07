from wagtail.admin.panels import Panel


class NewsletterPanel(Panel):
    clean_name = "newsletter_panel"  # type: ignore

    class BoundPanel(Panel.BoundPanel):
        template_name = "wagtail_newsletter/panels/newsletter_panel.html"
