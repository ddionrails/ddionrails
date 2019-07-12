# -*- coding: utf-8 -*-

""" "Index" management command for ddionrails project """

import json
import pathlib

import djclick as click
from django.conf import settings
from elasticsearch import Elasticsearch, helpers

from ddionrails.concepts.models import Concept
from ddionrails.data.models import Variable
from ddionrails.instruments.models import Question
from ddionrails.publications.models import Publication
from ddionrails.studies.models import Study

elasticsearch_client = Elasticsearch(hosts=[settings.INDEX_HOST])


def create(mapping_file: str) -> None:
    """ Create an Elasticsearch index

        using:
            - settings.INDEX_HOST
            - settings.INDEX_NAME
            - mapping_file
    """
    if elasticsearch_client.indices.exists(settings.INDEX_NAME):
        click.secho(f'Index "{settings.INDEX_NAME}" already exists.', fg="red")
        exit(1)
    else:
        if pathlib.Path(mapping_file).exists() is False:
            click.secho(f'Mapping file "{mapping_file}" not found.', fg="red")
            exit(1)
        else:
            with open(mapping_file, "r") as infile:
                mapping = json.load(infile)
            click.secho(
                f'Creating index "{settings.INDEX_NAME}" with maping from "{mapping_file}"',
                fg="green",
            )
            result = elasticsearch_client.indices.create(
                index=settings.INDEX_NAME, body=mapping
            )
            click.secho(str(result), fg="green")


def delete() -> None:
    """ Delete an Elasticsearch index

        using:
            - settings.INDEX_HOST
            - settings.INDEX_NAME
    """
    if elasticsearch_client.indices.exists(settings.INDEX_NAME):
        click.secho(f'Deleting index "{settings.INDEX_NAME}"', fg="green")
        result = elasticsearch_client.indices.delete(index=settings.INDEX_NAME)
        click.secho(str(result), fg="green")
    else:
        click.secho(f'Index "{settings.INDEX_NAME}" does not exist.', fg="red")
        exit(1)


def reset(mapping_file: str) -> None:
    """ Reset an Elasticsearch index

        using:
            - settings.INDEX_HOST
            - settings.INDEX_NAME
            - mapping_file
    """
    if pathlib.Path(mapping_file).exists() is False:
        click.secho(f'Mapping file "{mapping_file}" not found.', fg="red")
        exit(1)
    delete()
    create(mapping_file)


def concepts():
    """ Iterate over all concepts in the database """

    queryset = Concept.objects.prefetch_related("variables").all()
    for concept in queryset:
        study = list(
            Study.objects.filter(datasets__variables__concept_id=concept.id)
            .values_list("name", flat=True)
            .distinct()
        )
        yield {
            "_index": settings.INDEX_NAME,
            "_type": concept.DOC_TYPE,
            "_id": str(concept.id),
            "_source": {"name": concept.name, "label": concept.label, "study": study},
        }


def publications():
    """ Iterate over all publications in the database """

    queryset = Publication.objects.select_related("study").all()
    for publication in queryset:
        yield {
            "_index": settings.INDEX_NAME,
            "_type": publication.DOC_TYPE,
            "_id": str(publication.id),
            "_source": publication.to_elastic_dict(),
        }


def questions():
    """ Iterate over all questions in the database """

    queryset = Question.objects.select_related(
        "instrument",
        "instrument__analysis_unit",
        "instrument__period",
        "instrument__study",
    ).all()
    for question in queryset:
        period = question.get_period(period_id="name")
        try:
            analysis_unit = question.instrument.analysis_unit.name
        except AttributeError:
            analysis_unit = "None"
        yield {
            "_index": settings.INDEX_NAME,
            "_type": question.DOC_TYPE,
            "_id": str(question.id),
            "_source": {
                "period": period,
                "analysis_unit": analysis_unit,
                "question": question.name,
                "name": question.name,
                "label": question.label,
                "items": question.items,
                "sort_id": question.sort_id,
                "instrument": question.instrument.name,
                "study": question.instrument.study.name,
            },
        }


def variables():
    """ Iterate over all variables in the database """

    queryset = Variable.objects.select_related(
        "dataset",
        "dataset__study",
        "dataset__analysis_unit",
        "dataset__conceptual_dataset",
        "dataset__period",
    ).all()
    for variable in queryset:
        period = variable.get_period(period_id="name")
        try:
            analysis_unit = variable.dataset.analysis_unit.name
        except AttributeError:
            analysis_unit = "None"
        try:
            sub_type = variable.dataset.conceptual_dataset.name
        except AttributeError:
            sub_type = "None"

        yield {
            "_index": settings.INDEX_NAME,
            "_type": variable.DOC_TYPE,
            "_id": str(variable.id),
            "_source": {
                "name": variable.name,
                "variable": variable.name,
                "label": variable.label,
                "label_de": variable.label_de,
                "dataset": variable.dataset.name,
                "period": period,
                "sub_type": sub_type,
                "analysis_unit": analysis_unit,
                "study": variable.dataset.study.name,
                "categories": variable.categories,
            },
        }


def populate():
    """ Workaround """
    print(f"Indexing {Publication.objects.count()} publications into Elasticsearch")
    result = helpers.bulk(elasticsearch_client, publications())
    print(result)

    print(f"Indexing {Concept.objects.count()} concepts into Elasticsearch")
    result = helpers.bulk(elasticsearch_client, concepts())
    print(result)

    print(f"Indexing {Question.objects.count()} questions into Elasticsearch")
    result = helpers.bulk(elasticsearch_client, questions())
    print(result)

    print(f"Indexing {Variable.objects.count()} variables into Elasticsearch")
    result = helpers.bulk(elasticsearch_client, variables())
    print(result)


@click.group()
def command():
    """ddionrails: Elasticsearch index creation/deletion/reset tool."""


@command.command(
    "create",
    short_help='Create the index defined in "settings.INDEX_NAME" and the given "mapping_file"',
)
@click.option(
    "-f",
    "--file",
    "mapping_file",
    default="ddionrails/elastic/mapping.json",
    help='Elasticsearch mapping file in JSON format (defaults to "ddionrails/elastic/mapping.json")',
)
def create_command(mapping_file: str) -> None:
    """ Create an Elasticsearch index

        using:\n
            - settings.INDEX_HOST\n
            - settings.INDEX_NAME\n
            - mapping_file
    """
    create(mapping_file)


@command.command("delete", short_help='Delete the index defined in "settings.INDEX_NAME"')
def delete_command():
    """ Delete an Elasticsearch index

        using:\n
            - settings.INDEX_HOST\n
            - settings.INDEX_NAME
    """
    delete()


@command.command(
    "reset",
    short_help='Reset the index defined in "settings.INDEX_NAME" and the given "mapping_file"',
)
@click.option(
    "-f",
    "--file",
    "mapping_file",
    default="ddionrails/elastic/mapping.json",
    help='Elasticsearch mapping file in JSON format (defaults to "ddionrails/elastic/mapping.json")',
)
def reset(mapping_file: str) -> None:
    """ Reset an Elasticsearch index

        using:\n
            - settings.INDEX_HOST\n
            - settings.INDEX_NAME\n
            - mapping_file
    """
    delete()
    create(mapping_file)


@command.command("populate", short_help="Populate the Elasticsearch index")
def populate_command() -> None:
    """ Populate the Elasticsearch index """
    populate()


# remove "verbosity", "settings", "pythonpath", "traceback", "color" options from django-click
command.params = command.params[:2] + command.params[7:]
