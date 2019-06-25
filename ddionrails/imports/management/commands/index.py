# -*- coding: utf-8 -*-

""" "Index" management command for ddionrails project """

import json
import pathlib

import djclick as click
from django.conf import settings
from elasticsearch import Elasticsearch

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
