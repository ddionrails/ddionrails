"""Views for the statistics data visualization app."""
from typing import Any, Dict

from django.conf import settings
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView

from ddionrails.concepts.models import Topic
from ddionrails.data.models.variable import Variable
from ddionrails.studies.models import Study


def statistics_detail_view(
    request: HttpRequest, study: Study, plot_type: str
) -> HttpResponse:
    """Render numerical and categorical statistics views."""
    statistics_server_url = f"{request.get_host()}{settings.STATISTICS_SERVER_URL}"
    context: Dict[str, Any] = {}
    context[
        "statistics_server_url"
    ] = f"{request.scheme}://{statistics_server_url}{plot_type}/"
    context["study"] = study
    context["server_metadata"] = {
        "url": context["statistics_server_url"],
        "study": study.name,
    }
    context["variable"] = Variable.objects.select_related("dataset").get(
        id=request.GET["variable"]
    )
    return render(request, "statistics/statistics_detail.html", context=context)


class StatisticsNavView(TemplateView):
    """Render overview for all numerical and categorical statistics views."""

    template_name = "statistics/statistics_navigation.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["api_metadata"] = {
            "url": self.request.build_absolute_uri(reverse("api:variable-list")),
            "study": context["study"].name,
        }

        statistics_variables = Variable.objects.exclude(statistics_data=None).filter(
            dataset__study=context["study"]
        )
        root_topics = Topic.objects.filter(study=context["study"], parent=None)

        context["topics"] = {
            topic.name: {"label": topic.label, "label_de": topic.label_de}
            for topic in root_topics
        }

        context["categorical_variables"] = {}
        context["numerical_variables"] = {}
        for variable in statistics_variables.filter(
            statistics_data__plot_type="categorical"
        ):
            context["categorical_variables"][
                variable.id
            ] = f"{variable.label_de}: {variable.name}"

        for variable in statistics_variables.filter(
            statistics_data__plot_type="numerical"
        ):
            context["numerical_variables"][
                variable.id
            ] = f"{variable.label_de}: {variable.name}"

        return context
