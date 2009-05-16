from django.db import models
from django.utils.translation import ugettext_lazy as _

from malnutrition.models import zone, case, facility
from malnutrition.models import provider, log, report

# basic patient and zone information
class Zone(zone.Zone):
    class Meta(zone.Zone.Meta):
        app_label = "sms"
        
class Facility(facility.Facility):
    class Meta(facility.Facility.Meta):
        app_label = "sms"

class Provider(provider.Provider):
    class Meta(provider.Provider.Meta):
        app_label = "sms"
        
class Case(case.Case):
    """ A generic case or patient table """
    class Meta(case.Case.Meta):
        app_label = "sms"     

    def get_dictionary(self):
        """ There are some different string requests in the Malawi app and some things from Kenya
        eg first_name and last_name are not there """
        gender_long = {"m":"male", "f":"female"}
        dct = {
            'gender_long': gender_long[self.gender.lower()],
            'raw_months': self.years_months()[1],
            'dob': self.dob.strftime("%d.%m.%Y"), 
            'mobile': self.mobile,
            'ref_id': self.ref_id
        }
        return dct

# basic report information
class Observation(report.Observation):
    class Meta(report.Observation.Meta):
        app_label = "sms"
 
class Report(report.Report):
    """ A generic report """
    class Meta(report.Report.Meta):
        app_label = "sms"

class ReportMalnutrition(report.ReportMalnutrition):
    """ A generic report """
    class Meta(report.ReportMalnutrition.Meta):
        app_label = "sms"

class MessageLog(log.MessageLog):
    """ Yes please we'll have a message log too """
    class Meta(log.MessageLog.Meta):
        app_label = "sms"