# -*- coding: utf-8 -*-

""" Views for ddionrails project """

from datetime import datetime
from typing import Optional

from babel.dates import format_date
from django.conf import settings
from django.shortcuts import render
from django.utils.functional import cached_property
from django.views.generic.base import TemplateView
from markdown import markdown

from ddionrails.base.models import News 


# exception is a required parameter
def bad_request(request, exception):  # pylint: disable=unused-argument
    """Custom HTTP 400 view"""
    response = render(request, "400.html")
    response.status_code = 400
    return response


# exception is a required parameter
def permission_denied(request, exception):  # pylint: disable=unused-argument
    """Custom HTTP 403 view"""
    response = render(request, "403.html")
    response.status_code = 403
    return response


# exception is a required parameter
def page_not_found(request, exception):  # pylint: disable=unused-argument
    """Custom HTTP 404 view"""
    response = render(request, "404.html")
    response.status_code = 404
    return response


def server_error(request):
    """Custom HTTP 500 view"""
    response = render(request, "500.html")
    response.status_code = 500
    return response


class HomePageView(TemplateView):
    """Renders a list of all available studies."""

    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["news"] = self.news
        context["background_image"] = bool(settings.HOME_BACKGROUND_IMAGE)
        return context

    @cached_property
    def news(self) -> dict[str, str]:
        """Construct the html for the home news bubble.

        The start page displays a badge containing news about the development
        of the system itself and the study data contained in it.
        """
        news: dict[str, str] = {}
        _news_entry: Optional[News] = News.objects.first()
        if _news_entry is not None:
            news = self._format_news(_news_entry)
        return news

    @staticmethod
    def _format_news(news: News) -> dict[str, str]:
        date: datetime = news.date
        header_date = date.strftime("%B %Y")
        header_date_de = format_date(date, "MMMM Y", locale="de_DE")
        text_body = f"**Update {header_date}**\n\r" + news.content
        text_body_de = f"**Neuerungen {header_date_de}**\n\r" + news.content_de
        return {
            "en": markdown(text_body, extension=["nl2br"]),
            "de": markdown(text_body_de, extension=["nl2br"]),
        }
