# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods

""" Import resources for importing models from ddionrails.studies app into PostgreSQL


Authors:
    * 2019 Heinz-Alexander Fütterer (DIW Berlin)

License:
    | **AGPL-3.0 GNU AFFERO GENERAL PUBLIC LICENSE (AGPL) 3.0**.
    | See LICENSE at the GitHub
      `repository <https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md>`_
    | or at
      `<https://www.gnu.org/licenses/agpl-3.0.txt>`_.
"""

from import_export.resources import ModelResource

from .models import Study


class StudyResource(ModelResource):
    """ Import resource for studies.Study model """

    class Meta:  # pylint: disable=missing-docstring
        model = Study
        skip_unchanged = True
        report_skipped = True
        exclude = ("id", "created", "modified", "current_commit", "topic_languages")
        import_id_fields = ("name",)
