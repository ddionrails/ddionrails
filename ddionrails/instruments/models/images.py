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
from typing import Union

from django.conf import settings
from django.db import models
from filer.fields.image import FilerImageField

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

    #Django wants its identifier field to be named id
    #pylint: disable=invalid-name
    id = models.UUIDField(primary_key=True, editable=False)
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
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        """Adds creation of the value for the id field in front of the actual saving.

        This is done in order to make the id dependent on the objects.

        The arguments of this method are
        just passed on to the save() method of models.Model
        """
        _old_id = self.id

        # Get the question id if it is already set as UUID.
        try:
            _question_id = uuid.UUID(self.question_id)
        except (AttributeError, TypeError, ValueError):
            _question_id = self.question_id

        if not self.id_changed and isinstance(_question_id, uuid.UUID):
            self.id = uuid.uuid5(self.question, self.label + self.language)
        elif not self.id_changed and _question_id:
            self.id = uuid.uuid5(
                settings.UUID_BASE, str(_question_id) + self.label + self.language
            )
            LOGGER.warning(
                "QuestionImage %s:%s was set up without a UUID link to a question",
                self.image_id,
                self.label,
            )
        elif not (self.id_changed or self.question):
            self.id = uuid.uuid5(
                settings.UUID_BASE, self.label + self.language
            )
            LOGGER.warning(
                "QuestionImage %s:%s was set up without link to a question",
                self.image_id,
                self.label,
            )

        # Changing the value of the questions
        # ForeignKey will also change the PrimaryKey of the object.
        # To avoid duplicates we have to delete the object that still holds the old key.
        if _old_id:
            # To avoid problems, if id was changed only in memory.
            try:
                old = QuestionImage.objects.get(id=_old_id)
            except models.Model.DoesNotExist:
                _old_id = None
            else:
                old.delete()
        # Save normally
        super(QuestionImage, self).save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    def set_id(self, question_uuid: Union[str, uuid.UUID]) -> bool:
        """Sets the Objects PrimaryKey according to its own attributes and a UUID.

        Args:
            question_uuid (str, UUID): A UUID object or string representing a UUID.
                            Has to be the identifier of an instruments.Question
                            Object.
                            The Question objects existence will not be verifier here.
                            This should enable building of objects in memory to perform
                            bulk saves.
        Returns:
            bool: True if input was a UUID and the id could be set, False otherwise.
        """
        try:
            _uuid = uuid.UUID(str(question_uuid))
        except (AttributeError, TypeError, ValueError) as _error:
            LOGGER.exception(
                "Could not set %s id, %s is not a valid uuid.\n%s",
                __name__,
                question_uuid,
                _error,
            )
            return False

        self.id = uuid.uuid5(_uuid, self.label + self.language)
        self.question = str(_uuid)

        self.id_changed = True
        return True
