import pprint

from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView
from django.views.generic.base import RedirectView

from data.models import Variable
from studies.models import Study

from .models import Instrument, Question


def study_instrument_list(request, study_name):
    context = dict(
        study=Study.objects.get(name=study_name),
        instrument_list=Instrument.objects.filter(study__name=study_name),
    )
    return render(request, "instruments/study_instrument_list.html", context=context)


class InstrumentRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        instrument = get_object_or_404(Instrument, id=kwargs["id"])
        return instrument.get_absolute_url()


class InstrumentDetailView(DetailView):
    template_name = "instruments/instrument_detail.html"

    def get_object(self, queryset=None):
        instrument = get_object_or_404(
            Instrument,
            study__name=self.kwargs["study_name"],
            name=self.kwargs["instrument_name"],
        )
        return instrument

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["instrument"] = self.object  # TODO: redundant
        context["study"] = self.object.study
        context["questions"] = context["instrument"].questions.select_subclasses().all()
        return context


class QuestionRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        question = get_object_or_404(Question, id=kwargs["id"])
        return question.get_absolute_url()


def question_detail(request, study_name, instrument_name, question_name):
    question = (
        Question.objects.filter(instrument__study__name=study_name)
        .filter(instrument__name=instrument_name)
        .get(name=question_name)
    )

    concept_list = question.concept_list()
    try:
        related_questions = Question.objects.filter(
            items__items_variables__variable__concept_id__in=[
                concept.id for concept in concept_list
            ]
        ).distinct()
    except:
        related_questions = []
    context = dict(
        question=question,
        study=question.instrument.study,
        concept_list=concept_list,
        related_questions=related_questions,
        variables=Variable.objects.filter(questions_variables__question=question.id),
        debug_string=pprint.pformat(question.get_elastic(), width=120),
    )
    return render(request, "questions/question_detail.html", context=context)
