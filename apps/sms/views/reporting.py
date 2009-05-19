from malnutrition.forms import Form
from malnutrition.forms import DateField, StringField, GenderField
from malnutrition.sms.resolve import models

from malnutrition.sms.views.reporting import New, Report
from malnutrition.sms.command import authenticated, CommandError
from malnutrition.utils.parse import years_months

from apps.shortcuts import parser

class NewForm(Form):
    child = StringField(valid="(\d+)")
    gmc = StringField(valid="(\d+)")
    sex = GenderField()
    dob = DateField(format="%m%d%Y")
    dob.parser = parser
    contact = StringField(valid="(\d+)", required=False)
    
class MalawiNew(New):
    @authenticated
    def post_init(self):
        self.form = NewForm
    
    def pre_process(self):
        years, months = years_months(self.form.clean.dob.data)
        if years > 5:
            raise CommandError, "You have attempted to register child #%s. However, "\
                "the date of birth entered is %s. The age of this "\
                "child is above 5 years. Please resend SMS with corrected "\
                "age." % (self.form.clean.child.data, self.form.clean.dob.data.strftime("%m.%d.%Y"))
    
    def error_already_exists(self):
        return "You have attempted to register child #%s in %s GMC.  However, this child already exists.  If this is an error, please resend SMS with correct information. Please this child is a replacement, please confirm registration replying D (previous child died) or R (previous child replaced in program)." % (self.form.clean.child.data, self.data.provider.clinic.name)


class MalawiReport(Report):
    def success(self):
        info = self.data.case.get_dictionary()
        info.update(self.data.provider.get_dictionary())
        info.update(self.data.report.get_dictionary()) 
        info["status"] = "This child is healthy. Please thank the caregiver and remind her/him to return next month. "\
                         "If these measurements are not correct, please resend a corrected report immediately."
                         
        if self.data.report.status == self.data.report.MODERATE_STATUS:
            info["status"] = "This child has moderate acute malnutrition. Please refer to Supplementary Feeding Programme "\
                             "(SFP) and counsel caregiver on child nutrition."
                             
        if self.data.report.status in [self.data.report.SEVERE_STATUS, self.data.report.SEVERE_COMP_STATUS]:
            info["status"] = "This child has severe acute malnutrition. Please refer to a clinician "\
                             "immediately for admission into the NRU/TFP."

        if self.data.report.stunted:
            info["status"] = "This child is suffering from stunting. Please refer to the clinician immediately. %s" % info["status"]

        return "Thank you %(user_first_name)s %(user_last_name)s for reporting child #%(ref_id)s, "\
            "weight = %(weight)s, height = %(height)s, MUAC = %(muac)s, %(oedema)s oedema, %(diarrhea)s diarrhea. %(status)s" % info

    def not_valid(self, form):
        error_text = []
        for field in self.form.clean:
            if field.error:
                error_text.append("The %s entered is in error. Please correct the %s and resend a corrected report immediately." % (field.name, field.name))
        return "Thank you for reporting that child. %s" % " ".join(error_text)
        
    def post_process(self):
        # the Malawi report can only contain oedema and diarrhea
        report = self.data.report
        if self.form.clean.oedema.data:
            report.observed.add(models.Observation.objects.get(uid="oedema"))
            if report.status not in [report.SEVERE_STATUS, report.SEVERE_COMP_STATUS]:
                report.status = report.SEVERE_STATUS
                
        if self.form.clean.diarrhea.data:
            report.observed.add(models.Observation.objects.get(uid="diarrhea"))

        self.data.report.save()