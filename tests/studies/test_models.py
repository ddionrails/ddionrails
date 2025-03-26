# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name

""" Test cases for ddionrails.studies.models """

import unittest

import pytest
from django.test.testcases import LiveServerTestCase

from ddionrails.studies.models import Study, TopicList

pytestmark = [pytest.mark.studies, pytest.mark.models]

TEST_CASE = unittest.TestCase()


class TestStudyModel:
    def test_repo_url_method_https(self, study, settings):
        settings.GIT_PROTOCOL = "https"
        repo_url = study.repo_url()
        TEST_CASE.assertTrue(repo_url.startswith("https"))
        TEST_CASE.assertIn(study.repo, repo_url)

    def test_repo_url_method_ssh(self, study, settings):
        settings.GIT_PROTOCOL = "ssh"
        repo_url = study.repo_url()
        TEST_CASE.assertTrue(repo_url.startswith("git"))
        TEST_CASE.assertIn(study.repo, repo_url)

    def test_repo_url_method_exception(self, study, settings):
        settings.GIT_PROTOCOL = None
        with pytest.raises(Exception) as excinfo:
            study.repo_url()
            TEST_CASE.assertEqual(
                excinfo.value, "Specify a protocol for Git in your settings."
            )

    def test_has_topics_method_returns_true(self, study, topic):
        topic.study = study
        topic.save()
        TEST_CASE.assertTrue(study.has_topics())

    def test_set_topiclist_method(self, study):
        TEST_CASE.assertEqual(0, TopicList.objects.count())
        body = [{"topics": []}]
        study.set_topiclist(body)
        TEST_CASE.assertEqual(1, TopicList.objects.count())
        topiclist = TopicList.objects.first()
        TEST_CASE.assertEqual(study, topiclist.study)
        TEST_CASE.assertEqual(topiclist.topiclist, body)

    def test_get_topiclist_method(
        self, study, topiclist
    ):  # pylint: disable=unused-argument
        result = study.get_topiclist()
        expected = [{"title": "some-topic"}]
        TEST_CASE.assertEqual(expected, result)


@pytest.mark.usefixtures("study")
class TestStudyModelUnittset(LiveServerTestCase):
    study: Study

    def test_string_method(self):
        expected = self.study.name
        TEST_CASE.assertEqual(expected, str(self.study))

    def test_get_absolute_url_method(self):
        expected = f"/{self.study.name}/"
        TEST_CASE.assertEqual(expected, self.study.get_absolute_url())

    def test_has_topics_method(self):
        TEST_CASE.assertFalse(self.study.has_topics())

    def test_get_topiclist_method_without_topic_list(
        self,
    ):  # pylint: disable=unused-argument
        result = self.study.get_topiclist()
        self.assertIsNone(result)
