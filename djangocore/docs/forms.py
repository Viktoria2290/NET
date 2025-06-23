from django import forms
from .models import Docs

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Docs
        fields = ['file_path']
