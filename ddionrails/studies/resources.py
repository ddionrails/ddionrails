# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods

""" Import resources for ddionrails.studies app """

from import_export.resources import ModelResource

from .models import Study


class StudyResource(ModelResource):
    """ Import resource for studies.Study model """

    class Meta:  # pylint: disable=missing-docstring
        model = Study
        skip_unchanged = True
        report_skipped = True
        exclude = ("id",)
        import_id_fields = ("name",)
