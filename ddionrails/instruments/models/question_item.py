"""Define distinct question sections in the form of question items."""
import uuid
from typing import Any, Dict, Tuple

from django.db import models
from django.utils.translation import gettext_lazy as _

from ddionrails.instruments.models.question import Question


class QuestionItem(models.Model):
    """A question item is a section of a question, that is in itself a question."""

    class ItemScale(models.TextChoices):
        """Define possible item types."""

        TXT = "txt", _("Information Text")
        CAT = "cat", _("Multiple-answer multiple choice")
        BIN = "bin", _("Single-answer multiple choice")
        INT = "int", _("Integer")
        CHR = "chr", _("Open-ended")

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=True,
        db_index=True,
        help_text="UUID of the question. Dependent on the associated instrument.",
    )
    type = models.CharField(max_length=3, choices=ItemScale.choices)
    label = models.TextField(
        blank=True,
        verbose_name="Label (English)",
        help_text="Label of the question (English)",
    )
    label_de = models.TextField(
        blank=True,
        verbose_name="Label (German)",
        help_text="Label of the question (German)",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description (Markdown, English)",
        help_text="Description of the question (Markdown, English)",
    )
    description_de = models.TextField(
        blank=True,
        verbose_name="Description (Markdown, German)",
        help_text="Description of the question (Markdown, German)",
    )
    position = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Item position",
        help_text="Position of the question item within one question.",
    )

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answers: models.manager.Manager[Any]

    def delete(
        self, using: Any = None, keep_parents: bool = False
    ) -> Tuple[int, Dict[str, int]]:
        """Clean up related answers when deleting last related question item."""
        for _answer in self.answers.all():
            if len([_answer.question_items]) == 1:
                _answer.delete()
        return super().delete(using=using, keep_parents=keep_parents)
