from django.conf.urls.defaults import patterns, include
from django.contrib import admin

admin.autodiscover()

admin_urls = (r'^admin/(.*)', admin.site.root)

urlpatterns = patterns('',
    (r'^', include('rapidsms_baseui.urls')),
    admin_urls,
)