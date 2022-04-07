# -*- coding: utf-8 -*-

""" Importer classes for ddionrails.instruments app """

from csv import DictReader
from pathlib import Path
from typing import List

from ddionrails.instruments.models.question import Question
from ddionrails.studies.models import Study


def questions_images_import(file: Path, study: Study) -> None:
    "Initiate imports of all question images"
    if not file.exists():
        return
    with open(file, "r", encoding="utf8") as csv:
        reader = DictReader(csv)
        questions: List[Question] = []
        for index, row in enumerate(reader):
            question = Question.objects.get(
                instrument__study=study,
                instrument__name=row["instrument"],
                name=row["question"],
            )
            question.images = {
                "de": {"url": row["url_de"], "label": row["label_de"]},
                "en": {"url": row["url"], "label": row["label"]},
            }
            questions.append(question)
            if index % 1000:
                Question.objects.bulk_update(questions, ["question_images"])
                questions = []
        if questions:
            Question.objects.bulk_update(questions, ["question_images"])
