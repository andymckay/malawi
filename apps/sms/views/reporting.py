from django.utils.translation import ugettext
from django.contrib.auth.models import User
     
from apps.sms.models.base import Provider, Report, Case
from apps.sms.app import HandlerFailed, authenticated, _
from apps.shortcuts import parser

from malnutrition.forms import Form, BooleanField, DateField, StringField, GenderField

from datetime import date

class ReportForm(Form):
    child = StringField(valid="(\d+)")
    gmc = StringField(valid="(\d+)")
    sex = GenderField()
    dob = DateField(format="%m%d%Y")
    dob.parser = parser # custom data parser since the above format isn't like by strptime
    contact = StringField(valid="(\d+)", required=False)

@authenticated
def report(self, message, text):
    """ Report a child """
    report = ReportForm(text)
    if not report.is_valid():
        return message.respond("There was an error processing that. %s" % ". ".join(report.errors))
    
    provider = Provider.by_mobile(message.peer)
    try:
        Case.objects.get(ref_id=report.child.data, provider=provider)
        raise HandlerFailed(_("That child already exists."))
    except Case.DoesNotExist:
        case = Case(
            ref_id=report.child.data,
            provider=provider,
            mobile=report.contact.data,
            gender=report.sex.data,
            dob=report.dob.data
        )
        case.save()
        
        info = case.get_dictionary()
        info.update(provider.clinic.get_dictionary())
        return message.respond("Thank you for registering child #%(ref_id)s in %(name)s GMC, %(gender_long)s, age %(raw_months)s months, born %(dob)s, contact# %(mobile)s. If there is a mistake, please cancel this registration and try again." % info)