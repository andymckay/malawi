from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from apps.sms.models.base import Zone, Facility

class Profile(models.Model):
    PARTNER = 1
    NATIONAL = 2
    DISTRICT = 3
    GMC = 4
    ROLES = (
        (PARTNER, _('Partner')),
        (NATIONAL, _('National')),
        (DISTRICT, _('District')),
        (GMC, _('GMC')),
    )
    
    class Meta:
        app_label = "sms"
    
    user = models.ForeignKey(User, unique=True)
    # all these fields are optional, since they are just for the web interface
    zone = models.ForeignKey(Zone, null=True, blank=True)
    facility = models.ForeignKey(Facility, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLES, null=True, blank=True)

    def __unicode__(self):
        return self.user.first_name or str(self.user)

def create_profile(sender, **kw):
    user = kw["instance"]
    if kw["created"]:
        up = Profile(user=user)
        up.save()

post_save.connect(create_profile, sender=User)
