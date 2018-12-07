import pprint

from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView
from django.views.generic.base import RedirectView

from studies.models import Study

from .models import Publication


class PublicationRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        publication = get_object_or_404(Publication, id=kwargs["id"])
        return publication.get_absolute_url()


class PublicationDetailView(DetailView):
    model = Publication
    template_name = "publications/publication_detail.html"

    def get_object(self, queryset=None):
        publication = get_object_or_404(
            Publication,
            name=self.kwargs["publication_name"],
            study__name=self.kwargs["study_name"],
        )
        return publication

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bibtex"] = self.object.get_source()
        context["debug_string"] = pprint.pformat(self.object.get_elastic(), width=120)
        context["study"] = self.object.study
        context["links"] = [
            x.strip() for x in context["bibtex"].get("link", "").split(",")
        ]
        return context


def study_publication_list(request, study_name):
    context = dict(study=Study.objects.get(name=study_name))
    return render(request, "publications/study_publication_list.html", context=context)
