# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods,no-self-use,unused-argument

""" Import resources for importing models from ddionrails.concepts app into PostgreSQL


Authors:
    * 2019 Heinz-Alexander Fütterer (DIW Berlin)

License:
    | **AGPL-3.0 GNU AFFERO GENERAL PUBLIC LICENSE (AGPL) 3.0**.
    | See LICENSE at the GitHub
      `repository <https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md>`_
    | or at
      `<https://www.gnu.org/licenses/agpl-3.0.txt>`_.
"""

from import_export.fields import Field
from import_export.resources import ModelResource

from ddionrails.imports.helpers import (
    add_base_id_to_dataset,
    add_id_to_dataset,
    rename_dataset_headers,
)

from .models import AnalysisUnit, Concept, ConceptualDataset, Period, Topic


class TopicResource(ModelResource):
    """ Import resource for Topic model """

    study = Field(attribute="study_id", column_name="study_id")
    parent = Field(attribute="parent_id", column_name="parent_id")

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        """ Preprocess the whole dataset """
        rename_mapping = {"study_name": "study", "parent_name": "parent"}
        rename_dataset_headers(dataset, rename_mapping)

        # add study_id to dataset
        add_base_id_to_dataset(dataset, "study")
        add_id_to_dataset(dataset, "parent", "study_id")

    class Meta:  # pylint: disable=missing-docstring
        model = Topic
        skip_unchanged = True
        report_skipped = True
        exclude = ("id",)
        import_id_fields = ("study", "name")


class ConceptResource(ModelResource):
    """ Import resource for Concept model """

    def save_m2m(self, obj, data, using_transactions, dry_run):
        """ Save many to many relations (after creating new model instance) """
        topic_id = data.get("topic_id")
        if topic_id:
            obj.topics.add(topic_id)

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        """ Preprocess the whole dataset """
        rename_mapping = {"topic_name": "topic"}
        rename_dataset_headers(dataset, rename_mapping)

        # add study_id to dataset
        add_base_id_to_dataset(dataset, "study")
        add_id_to_dataset(dataset, "topic", "study_id")

    class Meta:  # pylint: disable=missing-docstring
        model = Concept
        skip_unchanged = True
        report_skipped = True
        exclude = ("id",)
        import_id_fields = ("name",)


class PeriodResource(ModelResource):
    """ Import resource for Period model """

    study = Field(attribute="study_id", column_name="study_id")

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        """ Preprocess the whole dataset """
        rename_mapping = {"period_name": "name", "study_name": "study"}
        rename_dataset_headers(dataset, rename_mapping)

        # add study_id to dataset
        add_base_id_to_dataset(dataset, "study")

    class Meta:  # pylint: disable=missing-docstring
        model = Period
        skip_unchanged = True
        report_skipped = True
        exclude = ("id",)
        import_id_fields = ("study", "name")


class AnalysisUnitResource(ModelResource):
    """ Import resource for AnalysisUnit model """

    study = Field(attribute="study_id", column_name="study_id")

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        """ Preprocess the whole dataset """
        rename_mapping = {"analysis_unit_name": "name", "study_name": "study"}
        rename_dataset_headers(dataset, rename_mapping)

        # add study_id to dataset
        add_base_id_to_dataset(dataset, "study")

    class Meta:  # pylint: disable=missing-docstring
        model = AnalysisUnit
        skip_unchanged = True
        report_skipped = True
        exclude = ("id",)
        import_id_fields = ("study", "name")


class ConceptualDatasetResource(ModelResource):
    """ Import resource for ConceptualDataset model """

    study = Field(attribute="study_id", column_name="study_id")

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        """ Preprocess the whole dataset """
        rename_mapping = {"conceptual_dataset_name": "name", "study_name": "study"}
        rename_dataset_headers(dataset, rename_mapping)

        # add study_id to dataset
        add_base_id_to_dataset(dataset, "study")

    class Meta:  # pylint: disable=missing-docstring
        model = ConceptualDataset
        skip_unchanged = True
        report_skipped = True
        exclude = ("id",)
        import_id_fields = ("study", "name")
