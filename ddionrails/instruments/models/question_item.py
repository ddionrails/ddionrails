"""Define distinct question sections in the form of question items."""
import uuid
from typing import Any, Dict, Iterable, List, Optional, Tuple, TypedDict

from django.db import models
from django.utils.translation import gettext_lazy as _

from ddionrails.imports.helpers import hash_with_namespace_uuid
from ddionrails.instruments.models.question import Question


class AnswerDict(TypedDict):
    """Typing for Answer dict representation"""

    value: int
    label: str
    label_de: str


class QuestionItemDict(TypedDict, total=False):
    """Typing for QuestionItem dict representation"""

    name: str
    scale: str
    label: str
    label_de: str
    description: str
    description_de: str
    instruction: str
    instruction_de: str
    position: int
    input_filter: str
    goto: str
    answers: List[AnswerDict]


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
        help_text="UUID of the QuestionItem. dependent on the associated Question.",
    )
    name = models.TextField(
        null=False,
        blank=False,
        verbose_name="Item name",
        help_text="Identifying name of the item.",
    )
    scale = models.CharField(max_length=3, choices=ItemScale.choices)
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
    instruction = models.TextField(
        blank=True,
        verbose_name="Instruction",
        help_text="Instruction given for this item.",
    )
    instruction_de = models.TextField(
        blank=True,
        verbose_name="Instruction",
        help_text="Instruction given for this item. (German)",
    )

    position = models.IntegerField(
        blank=False,
        null=False,
        verbose_name="Item position",
        help_text="Position of the question item within one question.",
    )
    input_filter = models.TextField(
        blank=True,
        null=True,
        verbose_name="Input Filter",
        help_text=(
            "Describes which question items lead to the inclusion of this question item."
        ),
    )
    goto = models.TextField(
        blank=True,
        null=True,
        verbose_name="Goto (Output Filter)",
        help_text="Describes which question item should follow this question item.",
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="question_items"
    )
    answers: models.manager.Manager[Any]

    def generate_id(self, cache=False):
        """Generate UUID used in the objects save method."""
        return hash_with_namespace_uuid(self.question_id, str(self.position), cache=cache)

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[Iterable[str]] = None,
    ) -> None:
        self.id = self.generate_id()  # pylint: disable=invalid-name
        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    def to_dict(self, short: bool = False) -> QuestionItemDict:
        """Map fields and values to dictionary key value pairs."""
        if short:
            self_dict = QuestionItemDict(
                label=self.label,
                label_de=self.label_de,
                instruction=self.instruction,
                instruction_de=self.instruction_de,
                scale=self.scale,
            )
        else:
            self_dict = QuestionItemDict(
                name=self.name,
                scale=self.scale,
                label=self.label,
                label_de=self.label_de,
                description=self.description,
                description_de=self.description_de,
                instruction=self.instruction,
                instruction_de=self.instruction_de,
                position=self.position,
                input_filter=self.input_filter,
                goto=self.goto,
            )
        if self.scale == "cat":
            self_dict["answers"] = [
                AnswerDict(
                    value=answer.value, label=answer.label, label_de=answer.label_de
                )
                for answer in self.answers.all().order_by("value").distinct()
            ]
        return self_dict

    def delete(
        self, using: Any = None, keep_parents: bool = False
    ) -> Tuple[int, Dict[str, int]]:
        """Clean up related answers when deleting last related question item."""
        for _answer in self.answers.all():
            if len([_answer.question_items]) == 1:
                _answer.delete()
        return super().delete(using=using, keep_parents=keep_parents)
