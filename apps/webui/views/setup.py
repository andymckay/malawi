from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.db.models import ObjectDoesNotExist

from apps.webui.forms.models import ProviderForm, UserForm
from apps.webui.forms.message import MessageForm
from apps.sms.models.base import Provider

from malnutrition.ui.views.shortcuts import as_html
from malnutrition.ui.views.shortcuts import login_required
from malnutrition.ui.views.message import message_users

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
def hsa_msg(request, object_id):
    provider = Provider.objects.get(id=object_id)
    message_form = MessageForm(request.POST or None)
    mobile = request.user.provider.mobile
    if message_form.is_valid():
        message_users(mobile=mobile, message=message_form.cleaned_data["message"], users=[provider.id,])
        
    return HttpResponseRedirect(provider.get_absolute_url())
    
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
    context["message_form"] = MessageForm(request.POST or None)
    
    try:
        context["mobile"] = request.user.provider.mobile
    except ObjectDoesNotExist:
        context["mobile"] = False
        
    context["object"] = provider
    return as_html(request, "user_edit_form.html", context)

