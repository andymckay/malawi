from django.utils.translation import ugettext
from django.contrib.auth.models import User
     
from apps.sms.models.base import Provider, Facility
from apps.sms.app import HandlerFailed, _

from malnutrition.forms import Form
from malnutrition.forms import BooleanField, DateField, StringField, GenderField, FloatField

class JoinForm(Form):
    last = StringField(valid="(.+)")
    first = StringField(valid="(.+)")
    gmc = StringField(valid="(\d+)")
    
def join(self, message, text):
    """ Join a USER based on spec. """
    # i believe GMC id is the clinic ID
    form = JoinForm(text)
    if not form.is_valid():
        return message.respond("There was an error processing that. %s" % ". ".join(form.errors))
        
    try:
        facility = Facility.objects.get(codename=form.gmc.data)
    except Facility.DoesNotExist:
        raise HandlerFailed(_("The GMC ID given does not exist."))

    mobile = message.peer
    in_use = Provider.by_mobile(mobile)
    
    if not in_use: 
        user = User(username="%s.%s" % (form.first.data, form.last.data), first_name=form.first.data, last_name=form.last.data)
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
    