# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

""" ModelForms for ddionrails.publications app """

from django import forms

from config.helpers import lower_dict_names

from .models import Attachment, Publication


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = (
            "study",
            "name",
            "sub_type",
            "title",
            "author",
            "year",
            "abstract",
            "cite",
            "url",
            "doi",
            "studies",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lower_dict_names(self.data)


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = (
            "context_study",
            "study",
            "dataset",
            "variable",
            "instrument",
            "question",
            "url",
            "url_text",
        )
