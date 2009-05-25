# import everything from rapidsms
from rapidsms.webui.settings import *
# now do overrides
DEBUG_MODE = False

# add in EGG based loading
TEMPLATE_LOADERS = list(TEMPLATE_LOADERS)
TEMPLATE_LOADERS.append('django.template.loaders.eggs.load_template_source')

# add in rapidsms_baseui
INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.append('malnutrition.ui')

TEMPLATE_CONTEXT_PROCESSORS = list(TEMPLATE_CONTEXT_PROCESSORS)
TEMPLATE_CONTEXT_PROCESSORS.append("apps.context.processor")

CACHE_BACKEND = 'file:///tmp/django_cache'

# the key for internal.rapidsms.ca, my testing internal domain
# insert your own keys below that
# get keys from: http://www.google.com/maps/api_signup
GOOGLE_MAPS_API_KEY = "ABQIAAAAkMK3-vxpvsIkaNV7-untGBSC6swhu1XNI82yHUogD0y_kw3SoxQD3OANi1rhbgZr6u-JERADbxbkVQ"