# -*- coding: utf-8 -*-

""" Importer classes for ddionrails.instruments app """

import logging
from csv import DictReader
from pathlib import Path
from typing import Dict, Optional

from ddionrails.imports.helpers import download_image, store_image
from ddionrails.instruments.models import Question, QuestionImage
from ddionrails.studies.models import Study

logging.config.fileConfig("logging.conf")  # type: ignore
logger = logging.getLogger(__name__)


def question_image_import(question: Question, image_data: Dict[str, str]) -> None:
    """Load and save the images of a Question

    Loads and saves up to two image files given their location by url.

    Args:
        question: The associated Question Object
        image_data: Contains "url" and/or "url_de" keys to locate image files.
                    Optionally contains "label" and/or "label_de" to add a label
                    to the corresponding images.
    """

    images = []

    if "url" in image_data:
        images.append(
            _question_image_import_helper(
                question,
                url=image_data["url"],
                label=image_data.get("label", None),
                language="en",
            )
        )
    if "url_de" in image_data:
        images.append(
            _question_image_import_helper(
                question,
                url=image_data["url_de"],
                label=image_data.get("label_de", None),
                language="de",
            )
        )

    for image in images:
        if image is not None:
            image.save()


def _question_image_import_helper(
    question: Question, url: str, label: Optional[str], language: str
) -> Optional[QuestionImage]:
    """Create a QuestionImage Object, load and store Image file inside it

    Args:
        question: The associated Question Object
        url: Location of the image to be loaded
        label: Is stored in the QuestionImage label field
        language: Is stored in the QuestionImage language field
    Returns:
        The QuestionImage created with loaded image.
        If the image could not be loaded, this will return None.
        QuestionImage is not written to the database here.
    """
    question_image = QuestionImage()
    instrument = question.instrument
    path = [instrument.study.name, instrument.name, question.name]
    _image = download_image(url)
    suffix = Path(url).suffix
    if label is None:
        label = "Screenshot"
    if _image is None:
        return None
    image, _ = store_image(file=_image, name=label + suffix, path=path)
    question_image.question = question
    question_image.image = image
    question_image.label = label
    question_image.language = language
    return question_image


def questions_images_import(file: Path, study: Study) -> None:
    "Initiate imports of all question images"
    if not file.exists():
        return
    with open(file, "r", encoding="utf8") as csv:
        reader = DictReader(csv)
        for row in reader:
            question = Question.objects.get(
                instrument__study=study,
                instrument__name=row["instrument"],
                name=row["question"],
            )
            question_image_import(question=question, image_data=row)
