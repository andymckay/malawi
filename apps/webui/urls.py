from django.conf.urls.defaults import patterns, include
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from django.views.generic.create_update import create_object, update_object

from apps.sms.models.base import Zone, Facility
from apps.webui.forms.models import GMCForm, ZoneForm

from django.contrib.auth.decorators import login_required

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'apps.webui.views.dashboard.view'),
    (r'^search/$', 'apps.webui.views.search.view'),
    (r'^zone/(?P<zone_id>\d+)/$', 'apps.webui.views.dashboard.view'),
    (r'^facility/(?P<facility_id>\d+)/$', 'apps.webui.views.dashboard.view'),
    (r'^district/$', 'apps.webui.views.tabs.district'),
    (r'^gmc/$', 'apps.webui.views.tabs.gmc'),
    (r'^gmc/edit/(?P<object_id>\d+)/$', login_required(update_object), {
        'template_name': 'edit_form.html',
        'form_class': GMCForm,
        'login_required': True,
        'post_save_redirect': '/setup/'
    }),
    (r'^gmc/add/$', login_required(create_object), {
        'template_name': 'add_form.html',
        'form_class': GMCForm,
        'login_required': True,
        'post_save_redirect': '/setup/'
    }),
    (r'^zone/edit/(?P<object_id>\d+)/$', login_required(update_object), {
        'template_name': 'edit_form.html',
        'form_class': ZoneForm,
        'login_required': True,
        'post_save_redirect': '/setup/'
    }),
    (r'^zone/add/$', login_required(create_object), {
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
    
    (r'^accounts/login/$', "apps.webui.views.login.login"),    
    
    # if nothing else matches
    (r'^', include('malnutrition.ui.urls')),
    (r'^admin/(.*)', admin.site.root),
)