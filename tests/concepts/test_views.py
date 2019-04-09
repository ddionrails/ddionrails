import pytest
from django.http.response import Http404
from django.urls import reverse

from ddionrails.concepts.views import ConceptDetail
from ddionrails.instruments.models import Question

pytestmark = [pytest.mark.concepts, pytest.mark.views]


@pytest.mark.django_db
class TestConceptDetailView:
    def test_concept_view_with_existing_concept_pk(self, rf, concept):
        url = reverse("concepts:concept_detail", kwargs={"pk": 1})
        request = rf.get(url)
        response = ConceptDetail.as_view()(request, pk=1)
        assert response.status_code == 200

    def test_concept_view_with_non_existing_concept_pk(self, rf, concept):
        url = reverse("concepts:concept_detail", kwargs={"pk": 999})
        request = rf.get(url)
        view = ConceptDetail.as_view()
        with pytest.raises(Http404):
            view(request, pk=999)

    def test_concept_view_with_existing_concept_name(self, client, concept):
        concept_name = "some-concept"
        url = reverse(
            "concepts:concept_detail_name", kwargs={"concept_name": concept_name}
        )
        response = client.get(url)
        assert response.status_code == 200
        template_name = "concepts/concept_detail.html"
        assert template_name in (t.name for t in response.templates)

        expected_variables = list(concept.variables.all())
        output_variables = list(response.context["variables"])
        assert output_variables == expected_variables

        expected_questions = list(
            Question.objects.filter(concepts_questions__concept_id=concept.id).all()
        )
        output_questions = list(response.context["questions"])
        assert output_questions == expected_questions

    def test_concept_view_with_non_existing_concept_name(self, rf, concept):
        concept_name = "missing-concept"
        url = reverse(
            "concepts:concept_detail_name", kwargs={"concept_name": concept_name}
        )
        request = rf.get(url)
        with pytest.raises(Http404):
            ConceptDetail.as_view()(request, concept_name=concept_name)
