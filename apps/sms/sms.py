from django.conf.urls.defaults import patterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^join (.*)', "apps.sms.views.joining.MalawiJoin"),
    (r'^new (.*?) cancel', "apps.sms.views.cancelling.MalawiNewCancel"),
    (r'^new (.*)', "apps.sms.views.reporting.MalawiNew"),
    (r'^report (.*)', "apps.sms.views.reporting.MalawiReport")
)