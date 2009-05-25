#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import sys, os
sys.path.append(os.path.join(os.getcwd(),'lib'))

# override the standard method for running this
# so that we can include settings.py and our own
# settings

from rapidsms.config import Config
from rapidsms.manager import Manager
from django.core.management import execute_manager, setup_environ

# we know it will be rapidsms.ini in this projects
os.environ["RAPIDSMS_INI"] = "rapidsms.ini" 
os.environ["DJANGO_SETTINGS_MODULE"] = "settings.py"

conf = Config(os.environ["RAPIDSMS_INI"])
import settings
setup_environ(settings) 

if sys.argv[1] == "test":
    from django.db.models.signals import post_save
    from django.contrib.auth.models import User
    from apps.sms.models.profile import create_profile
    post_save.disconnect(create_profile, sender=User)

if __name__ == "__main__":
    if hasattr(Manager, sys.argv[1]):
        handler = getattr(Manager(), sys.argv[1])
        handler(conf, *sys.argv[2:])
    elif settings:        
        execute_manager(settings)
