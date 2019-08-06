""" Implements a django model to store images for instruments.Question Objects


Authors:
    * 2019 Dominique Hansen (DIW Berlin)

License:
    | **AGPL-3.0 GNU AFFERO GENERAL PUBLIC LICENSE (AGPL) 3.0**.
    | See LICENSE at the GitHub
      `repository <https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md>`_
    | or at
      `<https://www.gnu.org/licenses/agpl-3.0.txt>`_.
"""

import logging
import uuid

from django.db import models
from filer.fields.image import FilerImageField

from ddionrails.imports.helpers import hash_with_namespace_uuid
from ddionrails.instruments.models.question import Question

LOGGER = logging.getLogger("django")


class QuestionImage(models.Model):
    """The QuestionImage model stores images to be displayed on question pages.

    Images are screnshots of questions as seen by study participants.
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
