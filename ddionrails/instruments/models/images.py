# -*- coding: utf-8 -*-
# This file is part of DDI on Rails.
#
# DDI on Rails is free software: you can redistribute it and/or modify
# it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# DDI on Rails is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU AFFERO GENERAL PUBLIC LICENSE for more details.
#
# You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
# along with DDI on Rails.  If not, see <https://www.gnu.org/licenses/>.
#
#
# - version   : >=3.2.0 (AGPLv3 License)
# - authors   :
#   - 2019 Dominique Hansen (DIW Berlin)
# - date      : 2019-06-11
# - copyright : Copyright (c) 2019, Dominique Hansen,
#               DIW Berlin <https://www.diw.de/>. All rights reserved.
# - license   : AGPL-3.0 GNU AFFERO GENERAL PUBLIC LICENSE (AGPL) 3.0.
#               See LICENSE at
#               <https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md>.
#               See AGPL License at
#               <https://www.gnu.org/licenses/agpl-3.0.txt>.

""" Implements a model to store images for instruments.Question Objects"""

import logging
import uuid

from django.db import models
from filer.fields.image import FilerImageField

from ddionrails.imports.helpers import hash_with_namespace_uuid
from ddionrails.instruments.models.question import Question

LOGGER = logging.getLogger("django")


class QuestionImage(models.Model):
    """
    The Image module is intended to store images for the display on question pages.

    Images are screnshots of questions.
    They are handled by django-filer and are linked here to a question via a foreign key.
    A question is linked to as many images as there are supported languages.

    Attributes:
        id (django.db.models.UUIDField): Primary key.
            Is generated on save from its attributs
            and its associated question.
        question (django.db.models.ForeignKey): Points to its question.
        image (filer.fields.FilerImageField): Foreign key.
            Points to the actual image.
        image_label (django.db.models.CharField): Natural language description.
            For display use.
        language (django.db.models.CharField): Language of the content displayed.
            Can accommodate language codes up to a length of two characters.
            It is intended to hold ISO 639-1 codes.
            A for a valid ISO 639-1 code is not performed.

    """

    # Django wants its identifier field to be named id
    # pylint: disable=invalid-name
    id = models.UUIDField(  # pylint: disable=C0103
        primary_key=True,
        default=uuid.uuid4,
        editable=True,
        db_index=True,
        help_text=("UUID of the QuestionImage. Dependent on the associated Question"),
    )
    question = models.ForeignKey(
        Question, blank=True, null=True, related_name="question", on_delete=models.CASCADE
    )
    image = FilerImageField(
        related_name="image", on_delete=models.CASCADE, null=False, blank=True
    )
    label = models.CharField(max_length=255)
    language = models.CharField(max_length=2)

    id_changed = False

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """"Set id and call parents save(). """
        self.id = hash_with_namespace_uuid(  # pylint: disable=C0103
            self.question_id, self.label + self.language, cache=False
        )
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )
