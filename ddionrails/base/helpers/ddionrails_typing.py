"""Provide typing functionality for all of ddionrails."""
from typing import List, TypedDict


class QuestionAnswer(TypedDict):
    """Represents an answer to a QuestionItem."""

    label: str
    label_de: str
    value: int


class QuestionItemType(TypedDict, total=False):
    """Define structure of a question item Dict.

    Inside the database, a question has a field with question items.
    This is a json field with a list of json objects.
    Every one of these objects is a question item.
    """

    answers: List[QuestionAnswer]
    concept: str
    instruction: str
    item: str
    number: str
    scale: str
    sn: int
    text_de: str
    text: str
