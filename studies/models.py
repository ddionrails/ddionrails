import json
import os
from json.decoder import JSONDecodeError

from django.conf import settings
from django.db import models
from django.urls import reverse
from model_utils.models import TimeStampedModel

from ddionrails.mixins import ModelMixin as DorMixin
from elastic.mixins import ModelMixin as ElasticMixin


class TopicList(ElasticMixin):

    DOC_TYPE = "topiclist"

    def __init__(self, study):
        self.id = study.id


class Study(ElasticMixin, DorMixin, TimeStampedModel):
    """
    Stores a single study,
    related to :model:`data.Dataset`, :model:`instruments.Instrument`,
    :model:`concepts.Period` and :model:`workspace.Basket`.
    """

    name = models.CharField(max_length=255, unique=True, db_index=True)
    label = models.CharField(max_length=255, blank=True)
    label_de = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True)
    repo = models.CharField(max_length=255, blank=True)
    webhook_token = models.CharField(max_length=255, blank=True)
    current_commit = models.CharField(max_length=255, blank=True)
    config = models.TextField(blank=True)
    files_url = models.CharField(max_length=255, blank=True)

    DOC_TYPE = "study"

    class DOR:
        io_fields = ["name", "label", "description"]
        id_fields = ["name"]

    def import_path(self):
        path = os.path.join(
            settings.IMPORT_REPO_PATH, self.name, settings.IMPORT_SUB_DIRECTORY
        )
        return path

    def repo_url(self):
        if settings.GIT_PROTOCOL == "https":
            url = "https://%s.git" % self.repo
        elif settings.GIT_PROTOCOL == "ssh":
            url = "git@%s.git" % self.repo
        else:
            raise Exception("Specify a protocol for Git in your settings.")
        return url

    def __str__(self):
        return "/%s" % self.name

    def get_absolute_url(self):
        return reverse("study_detail", kwargs={"study_name": self.name})

    def get_config(self, text=False):
        """
        The configuration is stored as a JSON object in a single text field in
        the database. If text==False, the configuration is returned as a
        dictonary, otherwise the text-representation as stored in the database
        will be returned.
        """
        if text:
            return self.config
        else:
            try:
                return json.loads(self.config)
            except JSONDecodeError:
                return []

    def set_topiclist(self, body):
        t = TopicList(self)
        t.set_elastic(body)

    def get_topic_languages(self):
        return self.get_source().get("topic_languages", [])

    def has_topics(self) -> bool:
        return len(self.get_topic_languages()) > 0

    def get_topiclist(self, language="en"):
        t = TopicList(self)
        all_lists = t.get_source().get("topiclist")
        for topiclist in all_lists:
            if topiclist.get("language", "") == language:
                return topiclist.get("topics")


def context(request):
    return dict(all_studies=Study.objects.all().only("name", "label", "description"))
