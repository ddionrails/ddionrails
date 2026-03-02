# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name

"""Test cases for ddionrails.studies.models"""

import unittest

import pytest
from django.test import TestCase, override_settings
from django.test.testcases import LiveServerTestCase

from ddionrails.studies.models import Study, TopicList
from tests.model_factories import StudyFactory, TopicFactory

pytestmark = [pytest.mark.studies, pytest.mark.models]

TEST_CASE = unittest.TestCase()


class TestStudyModel(TestCase):

    def setUp(self) -> None:
        self.study = StudyFactory()
        self.topic = TopicFactory(study=self.study)
        return super().setUp()

    @override_settings(GIT_PROTOCOL="https")
    def test_repo_url_method_https(self):
        repo_url = self.study.repo_url()
        self.assertTrue(repo_url.startswith("https"))
        self.assertIn(self.study.repo, repo_url)

    @override_settings(GIT_PROTOCOL="ssh")
    def test_repo_url_method_ssh(self):
        repo_url = self.study.repo_url()
        self.assertTrue(repo_url.startswith("git"))
        self.assertIn(self.study.repo, repo_url)

    @override_settings(GIT_PROTOCOL=None)
    def test_repo_url_method_exception(self):
        with pytest.raises(Exception) as excinfo:
            self.study.repo_url()
            self.assertEqual(
                excinfo.value, "Specify a protocol for Git in your settings."
            )

    def test_has_topics_method_returns_true(self):
        self.assertTrue(self.study.has_topics())

    def test_set_topiclist_method(self):
        self.assertEqual(0, TopicList.objects.count())
        body = [{"topics": []}]
        self.study.set_topiclist(body)
        self.assertEqual(1, TopicList.objects.count())
        topiclist = TopicList.objects.first()
        self.assertEqual(self.study, topiclist.study)
        self.assertEqual(topiclist.topiclist, body)

    def test_get_topiclist_method(self):
        expected = [{"title": self.topic.label}]
        topiclist = [{"language": "en", "topics": expected}]
        self.study.set_topiclist(topiclist)
        result = self.study.get_topiclist()
        self.assertEqual(expected, result)


class TestStudyModelUnittset(LiveServerTestCase):
    study: Study

    def setUp(self) -> None:
        self.study = StudyFactory()
        return super().setUp()

    def test_string_method(self):
        expected = self.study.name
        TEST_CASE.assertEqual(expected, str(self.study))

    def test_get_absolute_url_method(self):
        expected = f"/{self.study.name}/"
        TEST_CASE.assertEqual(expected, self.study.get_absolute_url())

    def test_has_topics_method(self):
        TEST_CASE.assertFalse(self.study.has_topics())

    def test_get_topiclist_method_without_topic_list(self):
        body = [{"topics": []}]
        self.study.set_topiclist(body)
        result = self.study.get_topiclist()
        self.assertIsNone(result)
