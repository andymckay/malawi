from django.utils.translation import ugettext
from django.contrib.auth.models import User
     
from apps.sms.models.base import Provider, Facility
from apps.sms.app import HandlerFailed, _

def join(self, message, last_name, first_name, gmc_id):
    """ Join a USER based on spec. """
    # i believe GMC id is the clinic ID
    try:
        facility = Facility.objects.get(codename=gmc_id)
    except Facility.DoesNotExist:
        raise HandlerFailed(_("The GMC ID given does not exist."))

    mobile = message.peer
    in_use = Provider.by_mobile(mobile)
    
    if not in_use: 
        user = User(username="%s.%s" % (first_name, last_name), first_name=first_name.title(), last_name=last_name.title())
        user.save()

        # ok its not in use, save it all and respond
        provider = Provider(mobile=mobile, user=user, clinic=facility, active=True)
        provider.save()
        
        info = provider.get_dictionary()
        info.update(facility.get_dictionary())
        return message.respond("Name = %(provider_name_inverted)s, GMC = %(name)s %(codename)s,"\
            " Phone number = %(mobile)s."\
            " If this is not correct, please re-register." % info)
    else:
        # so it's in use, don't save anything
        info = in_use.get_dictionary()
        info.update(facility.get_dictionary())
        return message.respond("An existing user %(provider_name_inverted)s at GMC #%(codename)s"\
            " is already registered to this phone number. "\
            " Confirm registration by replying N (for no) or Y (for yes)." % info)
    