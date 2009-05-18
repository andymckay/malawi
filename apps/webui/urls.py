from django.conf.urls.defaults import patterns, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'apps.webui.views.dashboard.view'),
    
    
    # if nothing else matches
    (r'^', include('malnutrition.ui.urls')),
    (r'^admin/(.*)', admin.site.root),
)