from django.utils.translation import ugettext
from django.contrib.auth.models import User
     
from apps.sms.models.base import Provider, ReportMalnutrition, Case, Observation
from apps.sms.app import HandlerFailed, authenticated, _
from apps.shortcuts import parser

from malnutrition.forms import Form
from malnutrition.forms import BooleanField, DateField, StringField, GenderField, FloatField

from datetime import date

class NewForm(Form):
    child = StringField(valid="(\d+)")
    gmc = StringField(valid="(\d+)")
    sex = GenderField()
    dob = DateField(format="%m%d%Y")
    dob.parser = parser # custom data parser since the above format isn't like by strptime
    contact = StringField(valid="(\d+)", required=False)

@authenticated
def new(self, message, text):
    """ Report a child """
    report = NewForm(text)
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
        return message.respond("Thank you for registering child #%(ref_id)s in %(name)s GMC,"\
            " %(gender_long)s, age %(raw_months)s months, born %(dob)s,"\
            " contact# %(mobile)s. If there is a mistake, please cancel"\
            " this registration and try again." % info)

class ReportForm(Form):
    child = StringField(valid="(\d+)")
    weight = FloatField()
    height = FloatField()
    muac = FloatField()
    oedema = BooleanField()
    diarrhea = BooleanField()

@authenticated
def report(self, message, text):
    form = ReportForm(text)
    if not form.is_valid():
        return message.respond("There was an error processing that. %s" % ". ".join(report.errors))
        
    provider = Provider.by_mobile(message.peer)
    
    try:
        case = Case.objects.get(ref_id=form.child.data, provider=provider)
    except Case.DoesNotExist:
        raise HandlerFailed(_("That child is not registered."))
  
    report = ReportMalnutrition(case=case, provider=provider, muac=form.muac.data, 
        weight=form.weight.data, height=form.height.data)
    report.save()
    
    if form.oedema.data:
        report.observed.add(Observation.objects.get(uid="oedema"))
    if form.diarrhea.data:
        report.observed.add(Observation.objects.get(uid="diarrhea"))
    
    report.save()
        