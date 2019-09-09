# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods,no-self-use,unused-argument

""" Import resources for importing models from ddionrails.instruments app into PostgreSQL


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
    add_concept_id_to_dataset,
    add_id_to_dataset,
    add_image_to_dataset,
    rename_dataset_headers,
)

from .models import ConceptQuestion, Instrument, Question, QuestionImage, QuestionVariable


class InstrumentResource(ModelResource):
    """ Import resource for Instrument model """

    # relations
    analysis_unit = Field(attribute="analysis_unit_id", column_name="analysis_unit_id")
    period = Field(attribute="period_id", column_name="period_id")
    study = Field(attribute="study_id", column_name="study_id")

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        """ Preprocess the whole dataset """
        rename_mapping = {
            "study_name": "study",
            "instrument_name": "name",
            "analysis_unit_name": "analysis_unit",
            "period_name": "period",
        }
        rename_dataset_headers(dataset, rename_mapping)

        # add study_id to dataset
        add_base_id_to_dataset(dataset, "study")
        add_id_to_dataset(dataset, "analysis_unit", "study_id")
        add_id_to_dataset(dataset, "period", "study_id")

    class Meta:  # pylint: disable=missing-docstring
        model = Instrument
        skip_unchanged = True
        report_skipped = True
        # id field is not imported
        exclude = ("id",)
        import_id_fields = ("study", "name")


class QuestionResource(ModelResource):
    """ Import resource for Question model """

    # relations
    instrument = Field(attribute="instrument_id", column_name="instrument_id")

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        """ Preprocess the whole dataset """
        rename_mapping = {"study_name": "study", "instrument_name": "instrument"}
        rename_dataset_headers(dataset, rename_mapping)

        # add study_id to dataset
        add_base_id_to_dataset(dataset, "study")
        add_id_to_dataset(dataset, "instrument", "study_id")

    class Meta:  # pylint: disable=missing-docstring
        model = Question
        skip_unchanged = True
        report_skipped = True
        # id field is not imported
        exclude = ("id",)
        import_id_fields = ("instrument", "name")


class ConceptQuestionResource(ModelResource):
    """ Import resource for ConceptQuestion model """

    # relations
    concept = Field(attribute="concept_id", column_name="concept_id")
    question = Field(attribute="question_id", column_name="question_id")

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        """ Preprocess the whole dataset """
        rename_mapping = {
            "study_name": "study",
            "instrument_name": "instrument",
            "question_name": "question",
            "concept_name": "concept",
        }
        rename_dataset_headers(dataset, rename_mapping)

        # add study_id to dataset
        add_base_id_to_dataset(dataset, "study")

        # add ids to dataset
        add_concept_id_to_dataset(dataset, "concept")
        add_id_to_dataset(dataset, "instrument", "study_id")
        add_id_to_dataset(dataset, "question", "instrument_id")

    class Meta:  # pylint: disable=missing-docstring
        model = ConceptQuestion
        skip_unchanged = True
        report_skipped = True
        # id field is not imported
        exclude = ("id",)
        import_id_fields = ("concept", "question")


class QuestionVariableResource(ModelResource):
    """ Import resource for QuestionVariable model """

    # relations
    question = Field(attribute="question_id", column_name="question_id")
    variable = Field(attribute="variable_id", column_name="variable_id")

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        """ Preprocess the whole dataset """
        rename_mapping = {
            "study_name": "study",
            "instrument_name": "instrument",
            "question_name": "question",
            "dataset_name": "dataset",
            "variable_name": "variable",
        }
        rename_dataset_headers(dataset, rename_mapping)

        # add study_id to dataset
        add_base_id_to_dataset(dataset, "study")

        # add instrument and question id, based on study id
        add_id_to_dataset(dataset, "instrument", "study_id")
        add_id_to_dataset(dataset, "question", "instrument_id")

        # add dataset and variable id, based on study id
        add_id_to_dataset(dataset, "dataset", "study_id")
        add_id_to_dataset(dataset, "variable", "dataset_id")

    class Meta:  # pylint: disable=missing-docstring
        model = QuestionVariable
        skip_unchanged = True
        report_skipped = True
        # id field is not imported
        exclude = ("id",)
        import_id_fields = ("question", "variable")


class QuestionImageResource(ModelResource):
    """ Import resource for QuestionImage model """

    # relations
    question = Field(attribute="question_id", column_name="question_id")

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        """ Preprocess the whole dataset """

        # add study_id to dataset
        add_base_id_to_dataset(dataset, "study")
        add_id_to_dataset(dataset, "instrument", "study_id")
        add_id_to_dataset(dataset, "question", "instrument_id")
        add_image_to_dataset(dataset)

    class Meta:  # pylint: disable=missing-docstring
        model = QuestionImage
        skip_unchanged = True
        report_skipped = True
        # id field is not imported
        exclude = ("id",)
        import_id_fields = ("question", "image")
