from malnutrition.ui.forms.base import BaseForm, BaseModelForm
from django import forms

class FilterForm(BaseForm):
    zone = forms.ChoiceField(
        widget=forms.Select(),
        required=False
    )