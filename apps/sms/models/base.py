from malnutrition.models import zone, case, facility
from malnutrition.models import provider, log, report

# basic patient and zone information
class Zone(zone.Zone):
    class Meta(zone.Zone.Meta):
        app_label = "sms"

    def get_absolute_url(self):
        return "/zone/edit/%s/" % self.id
        
class Facility(facility.Facility):
    class Meta(facility.Facility.Meta):
        app_label = "sms"

    def get_absolute_url(self):
        return "/gmc/edit/%s/" % self.id
    
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

    def get_absolute_url(self):
        return "/child/view/%s/" % self.id

    def months(self):
        return self.years_months()[-1]

# basic report information
class Observation(report.Observation):
    class Meta(report.Observation.Meta):
        app_label = "sms"

class ReportMalnutrition(report.ReportMalnutrition):
    """ A generic report """
    class Meta(report.ReportMalnutrition.Meta):
        app_label = "sms"
        ordering = ("-entered_at", )

    def get_dictionary(self):
        """ Return the data as a generic dictionary with some useful convenience methods done """
        dct = report.Report.get_dictionanry(self)
        dct.update({"oedema":"no", "diarrhea":"no"})
        if self.observed.filter(name="Oedema"):
            dct["oedema"] = "yes"
        if self.observed.filter(name="Diarrhea"):
            dct["diarrhea"] = "yes"

        return dct

class Provider(provider.Provider):
    class Meta(provider.Provider.Meta):
        app_label = "sms"

    def get_dictionary(self):
        """ Return the data as a generic dictionary with some useful convenience methods done """
        data = {
                "user_first_name": self.user.first_name,
                "user_last_name": self.user.last_name,
            }
        dct = provider.Provider.get_dictionary(self)
        dct.update(data)
        return dct
 
    def get_absolute_url(self):
        return "/hsa/edit/%s/" % self.id
 
    def quantity(self):
        return ReportMalnutrition.objects.filter(provider=self).count()

class MessageLog(log.MessageLog):
    """ Yes please we'll have a message log too """
    class Meta(log.MessageLog.Meta):
        app_label = "sms"