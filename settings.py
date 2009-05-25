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
TEMPLATE_CONTEXT_PROCESSORS.append("django.core.context_processors.auth")

CACHE_BACKEND = 'file:///tmp/django_cache'

AUTH_PROFILE_MODULE = (
    "sms.Profile"
)

# the key for internal.rapidsms.ca, my testing internal domain
# insert your own keys below that
# get keys from: http://code.google.com/apis/maps/signup.html
GOOGLE_MAPS_API_KEY = "ABQIAAAAkMK3-vxpvsIkaNV7-untGBSC6swhu1XNI82yHUogD0y_kw3SoxQD3OANi1rhbgZr6u-JERADbxbkVQ"
# rapidsms.clearwind.ca
#GOOGLE_MAPS_API_KEY = "ABQIAAAAkMK3-vxpvsIkaNV7-untGBSbQhILBHElm53TAoT1Du1fwqBJ4xSyFch-trgtqU7FG0XmQCLRE6f6YA"