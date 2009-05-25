from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect
from django.db.models import Q

from apps.webui.forms.models import ProviderForm, UserForm
from apps.sms.models.base import Provider

from malnutrition.ui.views.shortcuts import as_html
from malnutrition.ui.views.shortcuts import login_required

from reusable_table.table import get_dict

# zones vary by project
@login_required
@user_passes_test(lambda u: u.is_staff )
def hsa_add(request):
    context = {}
    if request.POST:
        provider_form = ProviderForm(request.POST)
        user_form = UserForm(request.POST)
        if provider_form.is_valid() and user_form.is_valid():
            user = user_form.save()
            provider = provider_form.save(commit=False)
            provider.user = user
            provider.save()
            return HttpResponseRedirect("/hsa/")
    else:
        provider_form = ProviderForm()
        user_form = UserForm()
    
    context["provider_form"] = provider_form
    context["user_form"] = user_form

    return as_html(request, "user_add_form.html", context)

@login_required
@user_passes_test(lambda u: u.is_staff )
def hsa_edit(request, object_id):
    provider = Provider.objects.get(id=object_id)
    context = {}
    if request.POST:
        provider_form = ProviderForm(request.POST, instance=provider)
        user_form = UserForm(request.POST, instance=provider.user)
        if provider_form.is_valid() and user_form.is_valid():
            user_form.save()
            provider_form.save()
            return HttpResponseRedirect("/hsa/")
    else:
        provider_form = ProviderForm(instance=provider)
        user_form = UserForm(instance=provider.user)
    
    context["provider_form"] = provider_form
    context["user_form"] = user_form
    context["object"] = provider
    return as_html(request, "user_edit_form.html", context)

