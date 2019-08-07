# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use

""" Test cases for importer classes in ddionrails.concepts app """

import pytest

from ddionrails.concepts.imports import TopicJsonImport
from ddionrails.studies.models import TopicList

pytestmark = [pytest.mark.concepts, pytest.mark.imports]  # pylint: disable=invalid-name


@pytest.fixture
def filename():
    return "DUMMY.csv"


@pytest.fixture
def topic_json_importer(db, filename, study):  # pylint: disable=unused-argument
    """ A topic json importer """
    return TopicJsonImport(filename, study)


class TestTopicJsonImport:
    def test_execute_import_method(self, topic_json_importer, mocker):
        """ Test that JSON string gets converted to dictionary and "_import_topic_list" gets called """
        mocked_import_topic_list = mocker.patch.object(
            TopicJsonImport, "_import_topic_list"
        )
        topic_json_importer.content = '[{"language": "en"}]'
        topic_json_importer.execute_import()
        assert topic_json_importer.content == [{"language": "en"}]
        mocked_import_topic_list.assert_called_once()

    def test_import_topic_list_method(self, topic_json_importer):
        """ Test that _import_topic_list adds "topic_languages" to Study object and creates a TopicList object """
        study = topic_json_importer.study
        assert [] == study.topic_languages
        assert 0 == len(study.topic_languages)
        assert 0 == TopicList.objects.count()
        topic_json_importer.content = [
            {"language": "en", "topics": []},
            {"language": "de", "topics": []},
        ]
        topic_json_importer._import_topic_list()  # pylint: disable=protected-access
        study.refresh_from_db()
        assert ["de", "en"] == study.topic_languages
        assert 1 == TopicList.objects.count()
        assert topic_json_importer.content == study.topiclist.topiclist
