from django.utils.translation import ugettext_lazy as _
from django import forms

from malnutrition.ui.forms.base import BaseForm

class MessageForm(BaseForm):
    message = forms.CharField(
        label = _("Message text"),
        required = True
    )