# -*- coding: utf-8 -*-
""" Index management command for ddionrails project """

import json

import djclick as click
from django.conf import settings
from elasticsearch import Elasticsearch

elasticsearch_client = Elasticsearch(hosts=[settings.INDEX_HOST])


def create() -> None:
    """ Create a Elasticsearch index

        using:
            - settings.INDEX_HOST
            - settings.INDEX_NAME
    """
    if elasticsearch_client.indices.exists(settings.INDEX_NAME):
        print(f'Index "{settings.INDEX_NAME}" already exists.')
    else:
        mapping_file = "ddionrails/elastic/mapping.json"
        with open(mapping_file, "r") as f:
            mapping = json.load(f)
        print(f'Deleting index "{settings.INDEX_NAME}" with maping from "{mapping_file}"')
        result = elasticsearch_client.indices.create(
            index=settings.INDEX_NAME, body=mapping
        )
        print(result)


def delete() -> None:
    """ Delete a Elasticsearch index

        using:
            - settings.INDEX_HOST
            - settings.INDEX_NAME
    """
    if elasticsearch_client.indices.exists(settings.INDEX_NAME):
        print(f'Deleting index "{settings.INDEX_NAME}"')
        result = elasticsearch_client.indices.delete(index=settings.INDEX_NAME)
        print(result)
    else:
        print(f'Index "{settings.INDEX_NAME}" does not exist.')


def reset() -> None:
    """ Reset a Elasticsearch index

        using:
            - settings.INDEX_HOST
            - settings.INDEX_NAME
    """
    delete()
    create()


@click.group()
def command():
    """ddionrails: Elasticsearch index creation/deletion/reset tool."""


@command.command(
    "create",
    short_help='Create the index defined in "settings.INDEX_NAME" and "ddionrails/elastic/mapping.json"',
)
def create_command():
    """Create the index"""
    create()


@command.command("delete", short_help='Delete the index defined in "settings.INDEX_NAME"')
def delete_command():
    """Delete the index"""
    delete()


@command.command(
    "reset",
    short_help='Reset the index defined in "settings.INDEX_NAME" and "ddionrails/elastic/mapping.json"',
)
def reset_command():
    """Reset the index"""
    reset()
