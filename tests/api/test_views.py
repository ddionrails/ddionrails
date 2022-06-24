# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for views in ddionrails.api app """

import json
import unittest
from typing import Dict, List
from unittest.mock import PropertyMock, patch
from uuid import UUID, uuid4

import pytest
from django.test.client import Client
from rest_framework.test import APIClient, APIRequestFactory

from ddionrails.instruments.models.concept_question import ConceptQuestion
from ddionrails.workspace.models import Basket, BasketVariable
from tests import status
from tests.concepts.factories import ConceptFactory, TopicFactory
from tests.data.factories import DatasetFactory, VariableFactory
from tests.factories import UserFactory
from tests.instruments.factories import (
    InstrumentFactory,
    QuestionFactory,
    QuestionItemFactory,
)
from tests.studies.factories import StudyFactory
from tests.workspace.factories import BasketVariableFactory

LANGUAGE = "en"

TEST_CASE = unittest.TestCase()


@pytest.mark.usefixtures("client", "request")
@pytest.fixture(name="unittest_web_client")
def _client(request, client):
    if request.instance:
        request.instance.web_client = client
        yield
    return client


@pytest.fixture(name="variable_with_concept_and_topic")
def _variable_with_concept_and_topic(variable, concept, topic):
    """A variable with a related concept and topic"""
    concept.topics.add(topic)
    concept.save()
    variable.concept = concept
    variable.save()
    return variable, concept, topic


def response_is_json(response) -> bool:
    """Helper function to validate a response's content type is JSON"""
    expected_content_type = "application/json"
    return expected_content_type == response["content-type"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "language,expected",
    [("en", [{"title": "some-topic"}]), ("de", [{"title": "some-german-topic"}])],
)
def test_topic_tree(client, topiclist, language, expected):
    response = client.get(
        f"/api/topic-tree/?study={topiclist.study.name}&language={language}"
    )
    TEST_CASE.assertEqual(status.HTTP_200_OK, response.status_code)
    TEST_CASE.assertEqual(expected, response.json())
    response_is_json(response)


######## Test new API units


@pytest.mark.django_db
class TestBasketViewSet(unittest.TestCase):

    API_PATH = "/api/baskets/"
    variables: List[VariableFactory] = []
    request_factory: APIRequestFactory

    def setUp(self):
        self.request_factory = APIRequestFactory()

        self._init_self_variables()

        self.study = self.variables[0].dataset.study
        self.user = UserFactory(username="test-user")

        self.basket = Basket()
        self.basket.name = "test-basket"
        self.basket.study = self.study
        self.basket.user = self.user
        self.basket.save()

        self.basket_data = {
            "user_id": self.user.id,
            "study_id": str(self.study.id),
            "name": "expected_basket",
            "label": "expected label",
            "description": "expected description",
        }

        return super().setUp()

    def _init_self_variables(self):
        if self.variables:
            return None
        self.variables = []
        for number in range(1, 100):
            self.variables.append(VariableFactory(name=f"{number}"))
        return None

    def test_get_basket(self):
        """Can we get the test basket from the API?"""
        results = self._get_api_GET_content()
        baskets_names = [result["name"] for result in results]

        self.assertIn(self.basket.name, baskets_names)

    def test_returned_fields(self):
        """Define fields that need to be present in API response."""
        results = self._get_api_GET_content()
        baskets_names = [result["name"] for result in results]
        test_basket = results[baskets_names.index(self.basket.name)]

        direct_fields = ["id", "name", "label", "description"]

        for field in direct_fields:
            self.assertIn(field, test_basket)
            self.assertEqual(getattr(self.basket, field), test_basket[field])

        self.assertIn("user_id", test_basket)
        self.assertEqual(self.basket.user.id, test_basket["user_id"])

        self.assertIn("study_id", test_basket)
        self.assertEqual(self.basket.study.id, UUID(test_basket["study_id"]))

    def test_create_basket(self):
        """Can we create a basket through the API?"""
        client = APIClient()
        client.force_authenticate(user=self.user)
        client.post(self.API_PATH, self.basket_data, format="json")

        baskets = self._get_api_GET_content()
        result = [
            basket for basket in baskets if basket["name"] == self.basket_data["name"]
        ]
        self.assertEqual(1, len(result))

        result = result[0]
        for key, value in self.basket_data.items():
            self.assertEqual(value, result.get(key))

    def test_create_existing_basket(self):
        """Creating an existing basket should be answered with HTTP 409."""
        client = APIClient()
        client.force_authenticate(user=self.user)
        client.post(self.API_PATH, self.basket_data, format="json")
        result = client.post(self.API_PATH, self.basket_data, format="json")
        self.assertEqual(409, result.status_code)

    def test_create_basket_no_user(self):
        """Only a logged in user should be able to create a basket."""
        client = APIClient()
        request = client.post(self.API_PATH, self.basket_data, format="json")

        self.assertEqual(403, request.status_code)

    def test_create_basket_wrong_user(self):
        """Only user with permissions should be able to create a basket."""

        client = APIClient()
        request = client.post(self.API_PATH, self.basket_data, format="json")

        dummy_user = UserFactory(username="dummy")
        client.force_authenticate(user=dummy_user)
        request = client.post(self.API_PATH, self.basket_data, format="json")
        self.assertEqual(403, request.status_code)
        dummy_user.delete()

    def test_create_basket_superuser(self):
        """Only user with permissions should be able to create a basket."""

        client = APIClient()

        dummy_user = UserFactory(username="dummy")
        dummy_user.is_superuser = True
        dummy_user.save()

        client.force_authenticate(user=dummy_user)
        request = client.get(self.API_PATH)
        self.assertEqual(200, request.status_code)
        dummy_user.delete()

    def _get_api_GET_content(self) -> Dict[str, str]:
        client = APIClient()
        client.force_authenticate(user=self.user)
        request = client.get(self.API_PATH, format="json")
        return json.loads(request.content).get("results")


@pytest.mark.django_db
class TestQuestionViewSet(unittest.TestCase):

    API_PATH = "/api/questions/"
    client: APIClient

    def setUp(self):
        self.client = APIClient()
        self.concept = ConceptFactory(name="test-concept")
        self.topic = TopicFactory(name="test-topic")
        return super().setUp()

    def test_query_parameter_conflict(self):
        concept_name = self.concept.name
        topic_name = self.topic.name
        response = self.client.get(
            self.API_PATH + f"?concept={concept_name}&topic={topic_name}"
        )
        self.assertEqual(406, response.status_code)
        content = json.loads(response.content)
        self.assertIn("mutually exclusive", content["detail"])

        response = self.client.get(self.API_PATH + f"?topic={topic_name}")
        self.assertEqual(406, response.status_code)
        content = json.loads(response.content)
        self.assertIn("requires study parameter", content["detail"])

    def test_404_errors(self):
        study = "some-nonexistent-study"
        call_string = f"{self.API_PATH}?study={study}"
        self.assertEqual(404, self.client.get(call_string).status_code)

        concept = "some-nonexistent-concept"
        call_string = f"{self.API_PATH}?concept={concept}"
        self.assertEqual(404, self.client.get(call_string).status_code)

        topic = "some-nonexistent-topic"
        call_string = f"{self.API_PATH}?topic={topic}&study=dummy"
        self.assertEqual(404, self.client.get(call_string).status_code)

    def test_query_parameter_concept(self):
        concept_name = self.concept.name
        question_list = []

        for number in range(1, 11):
            _question = QuestionFactory(name=str(number))
            _question.save()
            ConceptQuestion(concept=self.concept, question=_question).save()
            question_list.append(_question)

        for number in range(11, 21):
            _question = QuestionFactory(name=str(number))
            question_list.append(_question)

        response = self.client.get(self.API_PATH + f"?concept={concept_name}")
        content = json.loads(response.content)
        self.assertEqual(10, len(content))

    def test_query_parameter_study(self):
        """Define study parameter behavior."""
        instrument = InstrumentFactory(name="different-instrument")
        study = StudyFactory(name="different-study")
        study_name = study.name
        instrument.study = study
        instrument.save()
        question_list = []

        for number in range(1, 11):
            _question = QuestionFactory(name=str(number))
            _question.instrument = instrument
            _question.save()
            question_list.append(_question)

        for number in range(11, 21):
            _question = QuestionFactory(name=str(number))
            question_list.append(_question)

        response = self.client.get(self.API_PATH + f"?study={study_name}")
        content = json.loads(response.content)
        self.assertEqual(10, len(content))

    def test_returned_fields(self):
        """Define fields that should be provided."""
        expected_fields = [
            "id",
            "name",
            "label",
            "label_de",
            "instrument_name",
            "study_name",
            "study_label",
            "instrument",
            "study",
        ]
        QuestionFactory(name="test_question")
        response = self.client.get(self.API_PATH)
        results = json.loads(response.content)
        question = results[0]
        self.assertListEqual(expected_fields, list(question.keys()))

    def test_get_variable_GET_data(self):
        """Is the get response as expected?"""
        question_amount = 10
        questions = []
        for number in range(1, question_amount + 1):
            questions.append(QuestionFactory(name=f"{number}"))
        response = self.client.get(self.API_PATH)
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual(question_amount, len(content))
        result_ids = [result["id"] for result in content]
        for question in questions:
            self.assertIn(str(question.id), result_ids)

    def test_scroll_limit(self):
        """There should be no scroll limit"""
        question_amount = 101
        questions = []
        for number in range(1, question_amount + 1):
            questions.append(QuestionFactory(name=f"{number}"))
        response = self.client.get(self.API_PATH)
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual(question_amount, len(content))


@pytest.mark.django_db
class TestDatasetViewSet(unittest.TestCase):

    API_PATH = "/api/datasets/"
    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()
        return super().setUp()

    def test_no_parameter(self) -> None:
        other_study = StudyFactory(name="some-other-study")
        dataset = DatasetFactory(name="some-dataset")
        other_dataset = DatasetFactory(name="some-other-dataset", study=other_study)

        response = self.client.get(self.API_PATH)
        content = json.loads(response.content)
        self.assertEqual(2, content["count"])
        result_dataset_names = [result["name"] for result in content["results"]]
        self.assertIn(getattr(dataset, "name"), result_dataset_names)
        self.assertIn(getattr(other_dataset, "name"), result_dataset_names)

    def test_study_name_parameter(self) -> None:
        dataset = DatasetFactory(name="some-dataset")
        study_name = getattr(dataset.study, "name")

        response = self.client.get(self.API_PATH + f"?study={study_name}")
        content = json.loads(response.content)
        self.assertEqual(1, content["count"])
        self.assertEqual(getattr(dataset, "name"), content["results"][0]["name"])


@pytest.mark.django_db
class TestInstrumentViewSet(unittest.TestCase):

    API_PATH = "/api/instruments/"
    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()
        return super().setUp()

    def test_no_parameter(self) -> None:
        other_study = StudyFactory(name="some-other-study")
        instrument = InstrumentFactory(name="some-instrument")
        other_instrument = InstrumentFactory(
            name="some-other-instrument", study=other_study
        )

        response = self.client.get(self.API_PATH)
        content = json.loads(response.content)
        self.assertEqual(2, content["count"])
        result_instrument_names = [result["name"] for result in content["results"]]
        self.assertIn(getattr(instrument, "name"), result_instrument_names)
        self.assertIn(getattr(other_instrument, "name"), result_instrument_names)

    def test_study_name_parameter(self) -> None:
        instrument = InstrumentFactory(name="some-instrument")
        study_name = getattr(instrument.study, "name")

        response = self.client.get(self.API_PATH + f"?study={study_name}")
        content = json.loads(response.content)
        self.assertEqual(1, content["count"])
        self.assertEqual(getattr(instrument, "name"), content["results"][0]["name"])


@pytest.mark.django_db
class TestVariableViewSet(unittest.TestCase):

    API_PATH = "/api/variables/"
    client: APIClient

    def setUp(self):
        self.client = APIClient()
        self.concept = ConceptFactory(name="test-concept")
        self.topic = TopicFactory(name="test-topic")
        self.concept.topics.add(self.topic)
        self.concept.save()
        return super().setUp()

    def test_query_parameter_conflict(self):
        concept_name = self.concept.name
        topic_name = self.topic.name
        response = self.client.get(
            self.API_PATH + f"?concept={concept_name}&topic={topic_name}"
        )
        self.assertEqual(406, response.status_code)
        content = json.loads(response.content)
        self.assertIn("mutually exclusive", content["detail"])

        response = self.client.get(self.API_PATH + f"?topic={topic_name}")
        self.assertEqual(406, response.status_code)
        content = json.loads(response.content)
        self.assertIn("requires study parameter", content["detail"])

    def test_404_errors(self):
        study = "some-nonexistent-study"
        call_string = f"{self.API_PATH}?study={study}"
        self.assertEqual(404, self.client.get(call_string).status_code)

        concept = "some-nonexistent-concept"
        call_string = f"{self.API_PATH}?concept={concept}"
        self.assertEqual(404, self.client.get(call_string).status_code)

        topic = "some-nonexistent-topic"
        call_string = f"{self.API_PATH}?topic={topic}&study=dummy"
        self.assertEqual(404, self.client.get(call_string).status_code)

    def test_query_parameter_concept(self):
        concept_name = self.concept.name
        variable_list = []

        for number in range(1, 11):
            _variable = VariableFactory(name=str(number))
            _variable.concept = self.concept
            _variable.save()
            variable_list.append(_variable)

        for number in range(11, 21):
            _variable = VariableFactory(name=str(number))
            variable_list.append(_variable)

        response = self.client.get(self.API_PATH + f"?concept={concept_name}")
        content = json.loads(response.content)
        self.assertEqual(10, len(content))

    def test_query_parameter_study(self):
        """Define study parameter behavior."""
        dataset = DatasetFactory(name="different-dataset")
        study = StudyFactory(name="different-study")
        study_name = study.name
        dataset.study = study
        dataset.save()
        variable_list = []

        for number in range(1, 11):
            _variable = VariableFactory(name=str(number))
            _variable.dataset = dataset
            _variable.save()
            variable_list.append(_variable)

        for number in range(11, 21):
            _variable = VariableFactory(name=str(number))
            variable_list.append(_variable)

        response = self.client.get(self.API_PATH + f"?study={study_name}")
        content = json.loads(response.content)
        self.assertEqual(10, len(content))

    def test_returned_fields(self):
        """Define fields that should be provided."""
        expected_fields = [
            "id",
            "name",
            "label",
            "label_de",
            "dataset_name",
            "study_name",
            "study_label",
            "dataset",
            "study",
            "position",
        ]
        VariableFactory(name="test_variable")
        response = self.client.get(self.API_PATH)
        results = json.loads(response.content)
        variable = results[0]
        self.assertListEqual(expected_fields, list(variable.keys()))

    def test_get_variable_GET_data(self):
        """Is the get response as expected?"""
        variable_amount = 10
        variables = []
        for number in range(1, variable_amount + 1):
            variables.append(VariableFactory(name=f"{number}"))
        response = self.client.get(self.API_PATH)
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual(variable_amount, len(content))
        result_ids = [result["id"] for result in content]
        for variable in variables:
            self.assertIn(str(variable.id), result_ids)

    def test_scroll_limit(self):
        """There should be no scroll limit"""
        variable_amount = 101
        variables = []
        for number in range(1, variable_amount + 1):
            variables.append(VariableFactory(name=f"{number}"))
        response = self.client.get(self.API_PATH + "?paginate=False")
        self.assertEqual(200, response.status_code)
        content = json.loads(response.content)
        self.assertEqual(variable_amount, len(content))


@pytest.mark.django_db
class TestBasketVariableSet(unittest.TestCase):

    API_PATH = "/api/basket-variables/"
    client: APIClient

    def setUp(self):
        self.client = APIClient()
        self.basket_variable = BasketVariableFactory()
        self.basket_variable.save()
        self.variable = self.basket_variable.variable
        self.basket = self.basket_variable.basket
        self.user = self.basket.user
        return super().setUp()

    def test_get_basket_variable_GET_data(self):
        """Can we get basket variable data."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.API_PATH)
        results = json.loads(response.content)["results"]
        basket = results[0]
        self.assertEqual(self.basket_variable.basket_id, basket["basket_id"])
        self.assertEqual(str(self.basket_variable.variable_id), basket["variable_id"])

    def test_get_basket_variable_GET_with_url_param(self):
        """Can we get a basket variable with url params"""
        self.client.force_authenticate(user=self.user)
        new_basket_variable = BasketVariable()
        new_basket_variable.basket = self.basket
        new_basket_variable.variable = VariableFactory(name="new_variable")
        new_basket_variable.save()

        response = self.client.get(
            self.API_PATH
            + f"?variable={new_basket_variable.variable.id}&basket={self.basket.id}"
        )
        results = json.loads(response.content)["results"]
        basket = results[0]
        self.assertEqual(self.basket.id, basket["basket_id"])
        self.assertEqual(str(new_basket_variable.variable.id), basket["variable_id"])

    def test_get_basket_variable_GET_data_as_superuser(self):
        """Can we get basket variable data."""
        superuser = UserFactory(username="super_tester")
        superuser.is_superuser = True
        superuser.save()
        self.client.force_authenticate(user=superuser)
        response = self.client.get(self.API_PATH)
        results = json.loads(response.content)["results"]
        basket = results[0]
        self.assertEqual(self.basket_variable.basket_id, basket["basket_id"])
        self.assertEqual(str(self.basket_variable.variable_id), basket["variable_id"])
        superuser.delete()

    def test_get_basket_variable_GET_data_unauthorized(self):
        """Can we get basket variable data."""
        response = self.client.get(self.API_PATH)
        self.assertEqual(403, response.status_code)

    def test_POST_basket_variables(self):
        """Can we fill a basket with variables?"""
        new_variable = VariableFactory(name="new-test-variable")
        new_variable.dataset = self.variable.dataset
        new_variable.save()
        post_data = {"basket": str(self.basket.id), "variables": [str(new_variable.id)]}

        self.client.force_authenticate(user=self.user)
        post_response = self.client.post(self.API_PATH, post_data, format="json")
        self.assertEqual(201, post_response.status_code)

        result = self.client.get(f"{self.API_PATH}")
        results = json.loads(result.content)["results"]

        self.assertIn(
            True, [result["variable_id"] == str(new_variable.id) for result in results]
        )

    def test_POST_basket_variables_no_permission(self):
        """Are permissions respected."""
        some_user = UserFactory(username="some_tester")
        new_variable = VariableFactory(name="new-test-variable")
        new_variable.dataset = self.variable.dataset
        new_variable.save()
        post_data = {"basket": str(self.basket.id), "variables": [str(new_variable.id)]}

        self.client.force_authenticate(user=some_user)
        post_response = self.client.post(self.API_PATH, post_data, format="json")
        self.assertEqual(403, post_response.status_code)

    def test_DELETE_basket_variables(self):
        """Can we delete a BasketVariable"""
        new_variable = VariableFactory(name="new-test-variable")
        new_variable.dataset = self.variable.dataset
        new_variable.save()
        post_data = {"basket": str(self.basket.id), "variables": [str(new_variable.id)]}

        self.client.force_authenticate(user=self.user)
        post_response = self.client.post(self.API_PATH, post_data, format="json")
        self.assertEqual(201, post_response.status_code)

        result = self.client.get(f"{self.API_PATH}")
        results = json.loads(result.content)["results"]

        self.assertIn(
            True, [result["variable_id"] == str(self.variable.id) for result in results]
        )

        basket_variable_id = BasketVariable.objects.get(
            basket_id=self.basket.id, variable_id=new_variable.id
        ).id

        self.client.delete(self.API_PATH + f"{basket_variable_id}/")
        result = self.client.get(f"{self.API_PATH}")
        results = json.loads(result.content)["results"]

        self.assertNotIn(
            True, [result["variable_id"] == str(new_variable) for result in results]
        )

    def test_DELETE_basket_variables_no_permission(self):
        """Can we fill a basket with variables?"""
        user = UserFactory(username="unauthorized")

        new_variable = VariableFactory(name="new-test-variable")
        new_variable.dataset = self.variable.dataset
        new_variable.save()
        post_data = {"basket": str(self.basket.id), "variables": [str(new_variable.id)]}

        self.client.force_authenticate(user=user)
        self.client.post(self.API_PATH, post_data, format="json")

        basket_variable = BasketVariable.objects.get(
            basket_id=self.basket.id, variable_id=self.variable.id
        )
        basket_variable_id = basket_variable.id

        response = self.client.delete(self.API_PATH + f"{basket_variable_id}/")
        self.assertEqual(403, response.status_code)

    def test_POST_basket_variables_by_topic_by_name(self):
        """Define how basket variable creation by topic should work."""
        topic = TopicFactory(name="parent-topic")
        child_topic = TopicFactory(name="parent-topic", parent=topic)
        concept = ConceptFactory(name="some-concept")
        concept.topics.set([child_topic])
        concept.save()
        variables = [VariableFactory(name="1"), VariableFactory(name="2")]
        variables[1].concept = concept
        variables[1].save()

        post_data = {"basket": str(self.basket.id), "topic": topic.name}
        self.client.force_authenticate(user=self.user)
        post_response = self.client.post(self.API_PATH, post_data, format="json")
        self.assertEqual(201, post_response.status_code)
        get_response = self.client.get(self.API_PATH)
        content = json.loads(get_response.content)
        result_ids = [result["variable_id"] for result in content["results"]]
        self.assertIn(str(variables[1].id), result_ids)
        self.assertNotIn(str(variables[0].id), result_ids)

    def test_POST_basket_variables_by_concept_name(self):
        """Define how basket variable creation by concept should work."""
        topic = TopicFactory(name="parent-topic")
        child_topic = TopicFactory(name="parent-topic", parent=topic)
        concept = ConceptFactory(name="some-concept")
        concept.topics.set([child_topic])
        concept.save()
        variables = [VariableFactory(name="1"), VariableFactory(name="2")]
        variables[1].concept = concept
        variables[1].save()

        post_data = {"basket": str(self.basket.id), "concept": concept.name}
        self.client.force_authenticate(user=self.user)
        post_response = self.client.post(self.API_PATH, post_data, format="json")
        self.assertEqual(201, post_response.status_code)
        get_response = self.client.get(self.API_PATH)
        content = json.loads(get_response.content)
        result_ids = [result["variable_id"] for result in content["results"]]
        self.assertIn(str(variables[1].id), result_ids)
        self.assertNotIn(str(variables[0].id), result_ids)

    def test_basket_variable_limit(self):
        """Define how the basket limit should work."""
        too_many_variables = [
            VariableFactory(name=str(number)) for number in range(1, 11)
        ]
        too_many_variable_ids = [str(variable.id) for variable in too_many_variables]
        with patch(
            "ddionrails.api.views.user_tools.BasketVariableSet.basket_limit",
            new_callable=PropertyMock,
        ) as basket_limit:
            basket_limit.return_value = 10
            post_data = {
                "basket": str(self.basket.id),
                "variables": too_many_variable_ids,
            }
            self.client.force_authenticate(user=self.user)
            post_response = self.client.post(self.API_PATH, post_data, format="json")
            self.assertEqual(406, post_response.status_code)

    def test_basket_variable_limit_topic_and_concept_POST(self):
        """Define how the basket limit should work."""
        too_many_variables = []
        topic = TopicFactory(name="test-topic")
        concept = ConceptFactory(name="test-concept")
        concept.topics.set([topic])
        concept.save()
        for number in range(1, 12):
            variable = VariableFactory(name=str(number))
            variable.concept = concept
            variable.save()
            too_many_variables.append(variable)

        with patch(
            "ddionrails.api.views.user_tools.BasketVariableSet.basket_limit",
            new_callable=PropertyMock,
        ) as basket_limit:
            basket_limit.return_value = 10
            post_data = {"basket": str(self.basket.id), "topic": topic.name}
            self.client.force_authenticate(user=self.user)
            post_response = self.client.post(self.API_PATH, post_data, format="json")
            self.assertEqual(406, post_response.status_code)
            self.assertIn(b"basket size limit", post_response.content)

            BasketVariable.objects.all().delete()

            post_data = {"basket": str(self.basket.id), "concept": concept.name}
            self.client.force_authenticate(user=self.user)
            post_response = self.client.post(self.API_PATH, post_data, format="json")
            self.assertEqual(406, post_response.status_code)
            self.assertIn(b"basket size limit", post_response.content)


@pytest.mark.django_db
@pytest.mark.usefixtures("unittest_web_client")
class TestQuestionComparison(unittest.TestCase):

    API_PATH = "/api/question-comparison/"
    client: APIClient
    web_client: Client

    def setUp(self):
        self.client = APIClient()

        self.from_question = QuestionFactory(name="some-question", sort_id=1)
        self.to_question = QuestionFactory(name="some-other-question", sort_id=2)
        QuestionItemFactory(question=self.from_question, name=self.from_question.name)
        QuestionItemFactory(question=self.to_question, name=self.to_question.name)
        return super().setUp()

    def test_with_valid_ids(self):
        response = self.client.get(
            f"{self.API_PATH}?questions={self.from_question.id},{self.to_question.id}"
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        content = response.content.decode("utf-8")
        self.assertIn(self.from_question.instrument.period.name, content)
        self.assertIn(self.to_question.instrument.period.name, content)
        self.assertIn(self.from_question.name, content)
        self.assertIn(self.to_question.name, content)

    def test_with_invalid_from_id(self):
        false_uuid = uuid4()
        response = self.client.get(
            f"{self.API_PATH}?questions={false_uuid},{self.to_question.id}"
        )
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_with_invalid_to_id(self):
        false_uuid = uuid4()
        response = self.client.get(
            f"{self.API_PATH}?questions={self.from_question.id},{false_uuid}"
        )
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)


@pytest.mark.django_db
@pytest.mark.usefixtures("unittest_web_client")
class TestSendFeedback(unittest.TestCase):

    API_PATH = "/api/feedback/"
    client: APIClient
    web_client: Client

    def setUp(self):
        self.client = APIClient()

        return super().setUp()

    @patch(
        "ddionrails.api.views.user_tools.FEEDBACK_TO_EMAILS", new={"invalid": "test@mail"}
    )
    def test_anonymous_feedback(self) -> None:
        with patch("ddionrails.api.views.user_tools.send_mail") as send_mail:
            data = {
                "anon-submit-button": "",
                "feedback": "feedback",
                "source": "",
                "feedback-type": "praise",
            }
            response = self.client.post(
                f"{self.API_PATH}?type=invalid",
                data=data,
                HTTP_REFERER="https://localhost",
            )
            self.assertEqual(status.HTTP_302_FOUND, response.status_code)
            send_mail.assert_called_once()
            self.assertIn(["test@mail"], send_mail.call_args.args)

    def test_missing_feedback_type(self) -> None:
        data = {
            "anon-submit-button": "",
            "feedback": "feedback",
            "source": "",
            "feedback-type": "praise",
        }
        response = self.client.post(
            f"{self.API_PATH}",
            data=data,
            HTTP_REFERER="https://localhost",
        )
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
