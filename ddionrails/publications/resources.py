# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods,no-self-use,unused-argument

""" Import resources for ddionrails.publications app """


from import_export import resources
from import_export.fields import Field

from ddionrails.imports.helpers import (
    add_id_to_dataset,
    hash_with_namespace_uuid,
    rename_dataset_headers,
)

from .models import Attachment, Publication


class PublicationResource(resources.ModelResource):
    """ Import resource for publications.Publication model """

    # relations
    study = Field(attribute="study_id", column_name="study_id")

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        """ Preprocess the whole dataset """
        rename_mapping = {"study_name": "study"}
        rename_dataset_headers(dataset, rename_mapping)

        # add study_id to dataset
        add_id_to_dataset(dataset, "study")

    class Meta:  # pylint: disable=missing-docstring
        model = Publication
        skip_unchanged = True
        report_skipped = True
        exclude = ("id",)
        import_id_fields = ("study", "name")


class AttachmentResource(resources.ModelResource):
    """ Import resource for publications.Attachment model """

    # relations
    context_study = Field(attribute="context_study_id", column_name="context_study_id")

    study = Field(attribute="study_id", column_name="study_id")
    dataset = Field(attribute="dataset_id", column_name="dataset_id")
    instrument = Field(attribute="instrument_id", column_name="instrument_id")

    variable = Field(attribute="variable_id", column_name="variable_id")
    question = Field(attribute="question_id", column_name="question_id")

    def before_import_row(self, row, **kwargs):
        """ Preprocess row """

        # remove study_id if type is not study
        # otherwise Django would create a relation to the study as well
        if row["type"] != ("study"):
            row["study_id"] = None

        if row["type"] == "dataset":
            row["dataset_id"] = hash_with_namespace_uuid(
                row["context_study_id"], row["dataset"]
            )

        if row["type"] == "instrument":
            row["instrument_id"] = hash_with_namespace_uuid(
                row["context_study_id"], row["instrument"]
            )

        if row["type"] == "variable":
            _dataset_id = hash_with_namespace_uuid(
                row["context_study_id"], row["dataset"]
            )
            row["variable_id"] = hash_with_namespace_uuid(_dataset_id, row["variable"])

        if row["type"] == "question":
            _instrument_id = hash_with_namespace_uuid(
                row["context_study_id"], row["instrument"]
            )
            row["question_id"] = hash_with_namespace_uuid(_instrument_id, row["question"])

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        """ Preprocess the whole dataset """
        rename_mapping = {
            "study_name": "study",
            "dataset_name": "dataset",
            "variable_name": "variable",
            "instrument_name": "instrument",
            "question_name": "question",
        }
        rename_dataset_headers(dataset, rename_mapping)

        # add study_id to dataset
        add_id_to_dataset(dataset, "study")
        # set context_study_id
        dataset.append_col(dataset["study_id"], header="context_study_id")
        # prepare empty columns
        dataset.append_col([None] * len(dataset), header="dataset_id")
        dataset.append_col([None] * len(dataset), header="instrument_id")
        dataset.append_col([None] * len(dataset), header="variable_id")
        dataset.append_col([None] * len(dataset), header="question_id")

    class Meta:  # pylint: disable=missing-docstring
        model = Attachment
        skip_unchanged = True
        report_skipped = True
        exclude = ("id",)
        import_id_fields = (
            "study",
            "dataset",
            "variable",
            "instrument",
            "question",
            "url",
            "url_text",
        )
