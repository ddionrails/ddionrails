""""Define answer object for categorical question items ."""
from typing import Iterable, Optional

from django.db import models

from ddionrails.imports.helpers import hash_with_base_uuid
from ddionrails.instruments.models.question_item import QuestionItem


class Answer(models.Model):
    """Answers for multiple choice question items."""

    id = models.UUIDField(primary_key=True)
    value = models.IntegerField()
    label = models.TextField()
    label_de = models.TextField()
    question_items = models.ManyToManyField(QuestionItem, related_name="answers")

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[Iterable[str]] = None,
    ) -> None:
        self.id = hash_with_base_uuid(  # pylint: disable=invalid-name
            f"{self.value}{self.label}{self.label_de}", cache=True
        )
        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )
