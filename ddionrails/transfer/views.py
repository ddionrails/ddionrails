"""Views for the transfer data visualization app."""
from typing import Any, Dict

from django.conf import settings
from django.views.generic import TemplateView

# Create your views here.
# -*- coding: utf-8 -*-


class CategoricalView(TemplateView):
    """Render categorical transfer server plots."""

    template_name = "transfer/categorical.html"

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        transfer_server_url = f"{self.request.get_host()}{settings.TRANSFER_SERVER_URL}"
        context = super().get_context_data(**kwargs)
        context["server_metadata"] = {"url": f"http://{transfer_server_url}categorical/"}
        return context
