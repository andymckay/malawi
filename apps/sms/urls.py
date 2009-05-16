from django.conf.urls.defaults import patterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^join (\S+) (\S+) (\d+)', "apps.sms.views.joining.join",),
    (r'^new (.*)', "apps.sms.views.reporting.report"),
)