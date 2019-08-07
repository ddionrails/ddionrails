# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods,no-self-use,unused-argument

""" Import resources for importing models from ddionrails.data app into PostgreSQL


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

from ddionrails.imports.helpers import add_id_to_dataset, rename_dataset_headers

from .models import Dataset, Transformation, Variable


class DatasetResource(ModelResource):
    """ Import resource for Dataset model """

    # relations
    study = Field(attribute="study_id", column_name="study_id")
    analysis_unit = Field(attribute="analysis_unit_id", column_name="analysis_unit_id")
    conceptual_dataset = Field(
        attribute="conceptual_dataset_id", column_name="conceptual_dataset_id"
    )
    period = Field(attribute="period_id", column_name="period_id")

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        """ Preprocess the whole dataset """
        rename_mapping = {
            "study_name": "study",
            "dataset_name": "name",
            "analysis_unit_name": "analysis_unit",
            "conceptual_dataset_name": "conceptual_dataset",
            "period_name": "period",
        }
        rename_dataset_headers(dataset, rename_mapping)

        # add study id to dataset
        add_id_to_dataset(dataset, "study")

        # add id to dataset
        add_id_to_dataset(dataset, "analysis_unit", "study_id")
        add_id_to_dataset(dataset, "conceptual_dataset", "study_id")
        add_id_to_dataset(dataset, "period", "study_id")

    class Meta:  # pylint: disable=missing-docstring
        model = Dataset
        skip_unchanged = True
        report_skipped = True
        # id field is not imported
        exclude = ("id",)
        # study and name identify a dataset in the file
        import_id_fields = ("study", "name")

    def get_queryset(self):
        return (
            self._meta.model.objects.all()
            .select_related("study", "analysis_unit", "conceptual_dataset", "period")
            .only(
                "name",
                "label",
                "label_de",
                "description",
                "boost",
                "study__name",
                "analysis_unit__name",
                "conceptual_dataset__name",
                "period__name",
            )
        )


class VariableResource(ModelResource):
    """ Import resource for Variable model """

    # relations
    concept = Field(attribute="concept_id", column_name="concept_id")
    dataset = Field(attribute="dataset_id", column_name="dataset_id")

    def before_import_row(self, row, **kwargs):
        """ Preprocess row """
        # TODO: Remove lower casing?
        row["name"] = row["name"].lower()

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        """ Preprocess the whole dataset """
        rename_mapping = {
            "study_name": "study",
            "dataset_name": "dataset",
            "variable_name": "name",
            "concept_name": "concept",
        }
        rename_dataset_headers(dataset, rename_mapping)

        # add study_id to dataset
        add_id_to_dataset(dataset, "study")

        # add sort_id to dataset
        dataset.append_col(list(range(len(dataset))), header="sort_id")

        # add dataset_ids and concept_ids to dataset
        add_id_to_dataset(dataset, "concept")
        add_id_to_dataset(dataset, "dataset", "study_id")

    class Meta:  # pylint: disable=missing-docstring
        model = Variable
        skip_unchanged = True
        report_skipped = True
        # id field is not imported
        # TODO: JSON Files contain "period". Is this different from the dataset's period at any time?
        exclude = ("id", "period")
        # study and name identify a dataset in the file
        import_id_fields = ("dataset", "name")


class TransformationResource(ModelResource):
    """ Import resource for Transformation model """

    origin = Field(attribute="origin_id", column_name="origin_variable_id")
    target = Field(attribute="target_id", column_name="target_variable_id")

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        """ Preprocess the whole dataset """
        rename_mapping = {
            "origin_study_name": "origin_study",
            "origin_dataset_name": "origin_dataset",
            "origin_variable_name": "origin_variable",
            "target_study_name": "target_study",
            "target_dataset_name": "target_dataset",
            "target_variable_name": "target_variable",
        }
        rename_dataset_headers(dataset, rename_mapping)

        add_id_to_dataset(dataset, "origin_study")
        add_id_to_dataset(dataset, "origin_dataset", "origin_study_id")
        add_id_to_dataset(dataset, "origin_variable", "origin_dataset_id")

        add_id_to_dataset(dataset, "target_study")
        add_id_to_dataset(dataset, "target_dataset", "target_study_id")
        add_id_to_dataset(dataset, "target_variable", "target_dataset_id")

    class Meta:  # pylint: disable=missing-docstring
        model = Transformation
        skip_unchanged = True
        report_skipped = True
        # id field is not imported
        exclude = ("id",)
        # study and name identify a dataset in the file
        import_id_fields = ("origin", "target")
