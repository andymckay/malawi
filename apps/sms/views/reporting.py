from malnutrition.sms.resolve import models
from malnutrition.sms.views.reporting import Report
from malnutrition.sms.command import authenticated
from malnutrition.sms.command import CommandError
from apps.shortcuts import last_month

class MalawiReport(Report):
    @authenticated
    def post_init(self):
        Report.post_init(self) 
     
    def error_not_registered(self):
        return "You have attempted to record information for a child that is not yet registerd. Please register the child using the NEW command before sending this report."
      
    def success(self):
        # hard code the zone, in case the provider 
        clinic = self.data.provider.clinic
        self.data.case.facility = clinic
        self.data.case.zone = clinic.parent()
        
        info = self.data.case.get_dictionary()
        info.update(self.data.provider.get_dictionary())
        info.update(self.data.report.get_dictionary())
        healthy = True
        info["status"] = "This child is healthy. Please thank the caregiver and remind her/him to return next month. "\
                         "If these measurements are not correct, please resend a corrected report immediately."
        
        if self.data.report.status == self.data.report.MODERATE_STATUS:
            healthy = False
            info["status"] = "This child has moderate acute malnutrition. Please refer to Supplementary Feeding Programme "\
                             "(SFP) and counsel caregiver on child nutrition."
                             
        if self.data.report.status in [self.data.report.SEVERE_STATUS, self.data.report.SEVERE_COMP_STATUS]:
            healthy = False
            info["status"] = "This child has severe acute malnutrition. Please refer to a clinician "\
                             "immediately for admission into the NRU/TFP."

        if self.data.report.stunted:
            healthy = False
            info["status"] = "This child is suffering from stunting. Please refer to the clinician immediately. %s" % info["status"]

        # need to check for persistent diarrhea, if they had
        # diarrhea, last month, let someone know
        start, end = last_month()
        reports = self.data.case.reportmalnutrition_set.filter(entered_at__gte=start, entered_at__lte=end)
        for report in reports:
            if report.observed.filter(uid="diarrhea"):
                # diarrhea is not exclusive of the rest
                if healthy:
                    info["status"] = "This child has persistent diarrhea. Please refer to the clinician immediately."
                else: 
                    info["status"] += " This child also has persistent diarrhea."

        return "Thank you %(user_first_name)s %(user_last_name)s for reporting child #%(ref_id)s, "\
            "weight = %(weight)s, height = %(height)s, MUAC = %(muac)s, %(oedema)s oedema, %(diarrhea)s diarrhea. %(status)s" % info

    def not_valid(self, form):
        error_text = []
        for field in self.form.clean:
            if field.error:
                error_text.append("The %s entered is in error. Please correct the %s and resend a corrected report immediately." % (field.name, field.name))
        return "Thank you for reporting that child. %s" % " ".join(error_text)
    
    def pre_process(self):
        # convert cm to mm
        self.form.clean.muac.data = int(self.form.clean.muac.data * 10.0)
    
    def post_process(self):
        # the Malawi report can only contain oedema and diarrhea
        report = self.data.report
        if self.form.clean.oedema.data:
            report.observed.add(models.Observation.objects.get(uid="oedema"))
            print "Setting", models.Observation.objects.get(uid="oedema")
            if report.status not in [report.SEVERE_STATUS, report.SEVERE_COMP_STATUS]:
                report.status = report.SEVERE_STATUS
                
        if self.form.clean.diarrhea.data:
            report.observed.add(models.Observation.objects.get(uid="diarrhea"))
            print "Setting", models.Observation.objects.get(uid="diarrhea")
        self.data.report.save()