from django.http import HttpResponseRedirect
from django.contrib import auth
from django.utils.translation import ugettext_lazy as _

from malnutrition.ui.forms.login import LoginForm
from malnutrition.ui.views.shortcuts import as_html

# override
# 
# this is because we have non-staff users who can't access the admin
# interface, but they can access the web site as per spec

messages = {
    "login_failed": _("Username or password did not match"),
    "logged_out": _("You have been logged out"),
}

def login(request):
    context = {}
    context["msg"] = messages.get(request.GET.get("msg", None))
    
    if request.method == "POST":
        form = LoginForm(request.POST)
        if not request.user.is_authenticated():
            if form.is_valid():
                user = auth.authenticate(
                    username=form.cleaned_data["username"], 
                    password=form.cleaned_data["password"])
                if user:
                    if user.is_active:
                        auth.login(request, user)
                        return HttpResponseRedirect("/")
                return HttpResponseRedirect("/accounts/login/?msg=login_failed")
    else:
        form = LoginForm()
        
    context["form"] = form
    return as_html(request, "login.html", context)
