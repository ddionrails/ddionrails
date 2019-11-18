"""Type definitions for the import App."""
# pragma: no cover
from typing import TypedDict


class QuestionsImages(TypedDict):
    """Map the fields expected to be in a questions_images.csv to a dict."""

    study: str
    instrument: str
    question: str
    url: str
    url_de: str
    label: str
    label_de: str
