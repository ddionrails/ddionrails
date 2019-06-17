# -*- coding: utf-8 -*-

""" Test cases for ModelAdmins in ddionrails.publications app """

import pytest
from django.urls import reverse

from tests import status

pytestmark = [pytest.mark.django_db]  # pylint: disable=invalid-name


def test_attachment_admin_list(
    admin_client, attachment
):  # pylint: disable=unused-argument
    """ Test the AttachmentAdmin changelist """
    url = reverse("admin:publications_attachment_changelist")
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_attachment_admin_detail(admin_client, attachment):
    """ Test the AttachmentAdmin change_view """
    url = reverse("admin:publications_attachment_change", args=(attachment.id,))
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_publication_admin_list(
    admin_client, publication
):  # pylint: disable=unused-argument
    """ Test the PublicationAdmin changelist """
    url = reverse("admin:publications_publication_changelist")
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_publication_admin_detail(admin_client, publication):
    """ Test the PublicationAdmin change_view """
    url = reverse("admin:publications_publication_change", args=(publication.id,))
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code
