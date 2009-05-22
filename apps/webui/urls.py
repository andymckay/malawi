from django.conf.urls.defaults import patterns, include
from django.contrib import admin
from apps.sms.models.base import Zone
from apps.webui.forms.models import GMCForm, ZoneForm
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'apps.webui.views.dashboard.view'),
    (r'^zone/(?P<zone_id>\d+)/$', 'apps.webui.views.dashboard.view'),
    (r'^district/$', 'django.views.generic.simple.direct_to_template', {
        'template': 'district.html', 
        'extra_context':{"districts":Zone.objects.filter(category=5).order_by("name")}
    }),
    (r'^gmc/$', 'django.views.generic.simple.direct_to_template', {
        'template': 'gmc.html', 
    }),
    (r'^gmc/edit/(?P<object_id>\d+)/$', 'django.views.generic.create_update.update_object', {
        'template_name': 'edit_form.html',
        'form_class': GMCForm,
        'login_required': True,
        'post_save_redirect': '/setup/'
    }),
    (r'^gmc/add/$', 'django.views.generic.create_update.create_object', {
        'template_name': 'add_form.html',
        'form_class': GMCForm,
        'login_required': True,
        'post_save_redirect': '/setup/'
    }),
    (r'^zone/edit/(?P<object_id>\d+)/$', 'django.views.generic.create_update.update_object', {
        'template_name': 'edit_form.html',
        'form_class': ZoneForm,
        'login_required': True,
        'post_save_redirect': '/setup/'
    }),
    (r'^zone/add/$', 'django.views.generic.create_update.create_object', {
        'template_name': 'add_form.html',
        'form_class': ZoneForm,
        'login_required': True,
        'post_save_redirect': '/setup/'
    }),
    
    (r'^hsa/edit/(?P<object_id>\d+)/$', 'apps.webui.views.setup.hsa_edit'),
    (r'^hsa/add/$', 'apps.webui.views.setup.hsa_add'),
    (r'^child/$', 'apps.webui.views.tabs.child_list'),
    (r'^child/view/(?P<object_id>\d+)/$', 'apps.webui.views.tabs.child_view'),
    (r'^hsa/$', 'apps.webui.views.tabs.hsa'),
    (r'^setup/$', 'apps.webui.views.tabs.setup'),
    
    # if nothing else matches
    (r'^', include('malnutrition.ui.urls')),
    (r'^admin/(.*)', admin.site.root),
)