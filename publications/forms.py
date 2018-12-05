from django import forms
from ddionrails.helpers import lower_dict_names
from .models import *

class PublicationForm(forms.ModelForm):

    class Meta:
        model = Publication
        fields = ["name", "label", "description", "study"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lower_dict_names(self.data)
