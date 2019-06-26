# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,invalid-name

""" Test cases for index management command for ddionrails project """

import pytest
from click.testing import CliRunner

from ddionrails.imports.management.commands import index


@pytest.fixture
def mocked_elasticsearch_client(mocker):
    """ Mocked Elasticsearch Client for test cases """
    return mocker.patch(
        "ddionrails.imports.management.commands.index.elasticsearch_client"
    )


@pytest.fixture
def mocked_create(mocker):
    """ Mocked create function for test cases """
    return mocker.patch("ddionrails.imports.management.commands.index.create")


@pytest.fixture
def mocked_delete(mocker):
    """ Mocked delete function for test cases """
    return mocker.patch("ddionrails.imports.management.commands.index.delete")


def test_index_command():
    """ Test index management command shows help """
    result = CliRunner().invoke(index.command)
    assert (
        "ddionrails: Elasticsearch index creation/deletion/reset tool." in result.output
    )
    assert "create" in result.output
    assert "delete" in result.output
    assert "reset" in result.output
    assert 0 == result.exit_code


@pytest.mark.parametrize("option", ("-h", "--help"))
def test_index_command_with_option(option):
    """ Test index management command shows help with "-h" and "--help" """
    result = CliRunner().invoke(index.command, option)
    assert (
        "ddionrails: Elasticsearch index creation/deletion/reset tool." in result.output
    )
    assert "create" in result.output
    assert "delete" in result.output
    assert "reset" in result.output
    assert 0 == result.exit_code


def test_create_argument(mocked_elasticsearch_client):
    """ Test index management create argument """
    mocked_elasticsearch_client.indices.exists.return_value = False
    result = CliRunner().invoke(index.command, ["create"])
    mocked_elasticsearch_client.indices.create.assert_called_once()
    expected_message = "Creating index"
    assert expected_message in result.output
    assert 0 == result.exit_code


def test_create_argument_index_already_exists(mocked_elasticsearch_client):
    """ Test index management create argument on already existing index """
    mocked_elasticsearch_client.indices.exists.return_value = True
    result = CliRunner().invoke(index.command, ["create"])
    expected_message = 'Index "dor" already exists.'
    assert expected_message in result.output
    assert 1 == result.exit_code


@pytest.mark.parametrize("option", ("-f", "--file"))
def test_create_argument_with_option_with_missing_mapping_file(
    mocked_elasticsearch_client, option
):
    """ Test index management create argument with missing mapping file """
    mocked_elasticsearch_client.indices.exists.return_value = False
    mapping_file = "mapping_file.json"
    result = CliRunner().invoke(index.command, ["create", option, mapping_file])
    expected_message = "not found"
    assert expected_message in result.output
    assert 1 == result.exit_code


def test_delete_argument_index_does_not_exist(mocked_elasticsearch_client):
    """ Test index management delete argument with non existing index """
    mocked_elasticsearch_client.indices.exists.return_value = False
    result = CliRunner().invoke(index.command, ["delete"])
    expected_message = 'Index "dor" does not exist.'
    assert expected_message in result.output
    assert 1 == result.exit_code


def test_delete_argument(mocked_elasticsearch_client):
    """ Test index management delete argument with existing index """
    mocked_elasticsearch_client.indices.exists.return_value = True
    result = CliRunner().invoke(index.command, ["delete"])
    mocked_elasticsearch_client.indices.delete.assert_called_once_with(index="dor")
    expected_message = "Deleting index"
    assert expected_message in result.output
    assert 0 == result.exit_code


def test_reset_argument(mocked_create, mocked_delete):
    """ Test index management reset argument """
    result = CliRunner().invoke(index.command, ["reset"])
    assert 0 == result.exit_code
    mocked_delete.assert_called_once()
    mocked_create.assert_called_once()


@pytest.mark.parametrize("option", ("-f", "--file"))
def test_reset_argument_with_option(mocked_create, mocked_delete, option):
    """ Test index management reset argument """
    mapping_file = "mapping_file.json"
    result = CliRunner().invoke(index.command, ["reset", option, mapping_file])
    assert 0 == result.exit_code
    mocked_delete.assert_called_once()
    mocked_create.assert_called_once()
