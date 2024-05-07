import json

from typing import cast

from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from wagtail.models import Page

from .models import NewsletterPageMixin


def send_test_email(request: HttpRequest, page_id):
    page = cast(NewsletterPageMixin, get_object_or_404(Page, pk=page_id).specific)
    email_address = json.loads(request.body)["email_address"]
    page.send_newsletter_test(email_address)
    return JsonResponse({"message": f"Successfully sent email to {email_address}"})
