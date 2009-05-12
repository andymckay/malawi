# import everything from rapidsms
from rapidsms.webui.settings import *
# now do overrides
DEBUG_MODE = False

# add in EGG based loading
TEMPLATE_LOADERS = list(TEMPLATE_LOADERS)
TEMPLATE_LOADERS.append('django.template.loaders.eggs.load_template_source')

# add in rapidsms_baseui
INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.append('rapidsms_baseui')

TEMPLATE_CONTEXT_PROCESSORS = list(TEMPLATE_CONTEXT_PROCESSORS)
TEMPLATE_CONTEXT_PROCESSORS.append("apps.context.processor")