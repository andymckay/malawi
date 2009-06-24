# -*- coding: utf-8 -*-
from rapidsms.tests.scripted import TestScript
from django.core.management import call_command
from django.test import TestCase
from datetime import datetime, timedelta
from app import App

from apps.sms.models.base import ReportMalnutrition, Case, MessageLog

def years_months(dt):
    dt = datetime.strptime(dt, "%d/%m/%Y").date()
    now = datetime.now().date()
    ymonths = (now.year - dt.year) * 12
    months = ymonths + (now.month - dt.month)
    return (now.year - dt.year, months)
    
loaded = False
class TestApp (TestScript):
    apps = (App,)
    fixtures = ("base.json", "auth.json", "observations.json")
    
    def setUp (self):
        # since the database is not nuked, there's no point in reloading these every time
        # this also messes up 13 and 14 which change the db
        # plus the unit tests are waaaay faster
        global loaded
        if not loaded and hasattr(self, "fixtures"):
            # borrowed from django/test/testcases.py
            call_command('loaddata', *self.fixtures, **{'verbosity': 0})            
            loaded = True

        TestScript.setUp(self)

    test_00_join = """
        # test joining as a user
        1234567 > JOIN 1202 Coulibaly Mariam 
        1234567 < The GMC ID given does not exist.
        
        1234567 > JOIN 1201 Coulibaly Mariam 
        1234567 < Name = Coulibaly Mariam, GMC = Salima 1201, Phone number = 1234567. If this is not correct, please re-register.
        
        1234569 > JOIN 1201 Danae McKay 
        1234569 < Name = Danae Mckay, GMC = Salima 1201, Phone number = 1234569. If this is not correct, please re-register.

        1234569 > JOIN 1201 Andy McKay 
        1234569 < An existing user Danae Mckay at GMC #1201 is already registered to this phone number. Reply with 'CONFIRM mandy-001'.
        
        1234569 > CONFIRM mandy-001
        1234569 < 1234569 registered to Andy Mckay at GMC #1201.
        
        1234569 > JOIN 1201 Danae McKay
        1234569 < An existing user Andy Mckay at GMC #1201 is already registered to this phone number. Reply with 'CONFIRM mdanae-001'.
    """
    
    test_01_registration = """
        # test registration
        1234568 > NEW 69 1201 M 19102008 09555123
        1234568 < 1234568 is not a registered number.
        
        1234567 > NEW 69 1201 M 19102008
        1234567 < You have attempted to register child #69 in Salima GMC. However, this child already exists. If this is an error, please resend SMS with correct information. If this patient is new or a replacement, please use the EXIT command first, then re-register.

        1234567 > NEW 70 1201 M 19102008 123124124
        1234567 < Thank you for registering child #70 in Salima GMC, male, age %s months, born 19.10.2008, contact# 123124124. If there is a mistake, please use EXIT to cancel this registration and try again.
        
        1234567 > NEW 70 1201 M 19102003 123124124
        1234567 < You have attempted to register child #70. However, the date of birth entered is 10.19.2003. The age of this child is above 5 years. Please resend SMS with corrected age.
    """ % (years_months("19/10/2008")[1])
    
    test_02_report = """
        # test reporting
        1234567 > REPORT 68 25.2 95.5 8.3 N Y
        1234567 < You have attempted to record information for a child that is not yet registerd. Please register the child using the NEW command before sending this report.
        
        1234567 > REPORT 70 Foo 95.5 8.3 N Y
        1234567 < Thank you for reporting that child. The weight entered is in error. Please correct the weight and resend a corrected report immediately.

        1234567 > REPORT 70 Foo 95.5 8.3 
        1234567 < Thank you for reporting that child. The weight entered is in error. Please correct the weight and resend a corrected report immediately. The oedema entered is in error. Please correct the oedema and resend a corrected report immediately. The diarrhea entered is in error. Please correct the diarrhea and resend a corrected report immediately.
        
        1234568 > REPORT 70 25.2 95.5 13 N Y
        1234568 < 1234568 is not a registered number.
        
        1234567 > REPORT 70 25.2 95.5 13 N Y
        1234567 < Thank you Mariam Coulibaly for reporting child #70, weight = 25.2 kg, height = 95.5 cm, MUAC = 13.0 cm, no oedema, yes diarrhea. This child is healthy. Please thank the caregiver and remind her/him to return next month. If these measurements are not correct, please resend a corrected report immediately.

        # high muac
        1234567 > REPORT 70 25.2 95.5 12.7 N Y
        1234567 < Thank you Mariam Coulibaly for reporting child #70, weight = 25.2 kg, height = 95.5 cm, MUAC = 12.7 cm, no oedema, yes diarrhea. This child is healthy. Please thank the caregiver and remind her/him to return next month. If these measurements are not correct, please resend a corrected report immediately.
                
        # low muac
        1234567 > REPORT 70 25.2 95.5 10 N Y
        1234567 < Thank you Mariam Coulibaly for reporting child #70, weight = 25.2 kg, height = 95.5 cm, MUAC = 10.0 cm, no oedema, yes diarrhea. This child has severe acute malnutrition. Please refer to a clinician immediately for admission into the NRU/TFP.
        
        # muac inbetween
        1234567 > REPORT 70 25.2 95.5 11.2 N Y
        1234567 < Thank you Mariam Coulibaly for reporting child #70, weight = 25.2 kg, height = 95.5 cm, MUAC = 11.2 cm, no oedema, yes diarrhea. This child has moderate acute malnutrition. Please refer to Supplementary Feeding Programme (SFP) and counsel caregiver on child nutrition.
        
        # low weight
        1234567 > REPORT 70 5.2 95.5 12.7 N Y
        1234567 < Thank you Mariam Coulibaly for reporting child #70, weight = 5.2 kg, height = 95.5 cm, MUAC = 12.7 cm, no oedema, yes diarrhea. This child has severe acute malnutrition. Please refer to a clinician immediately for admission into the NRU/TFP.
    """

    def test_02_report_test(self):
        case = Case.objects.get(ref_id=70)
        reports = ReportMalnutrition.objects.filter(case=case)
        # we keep deleting so we only have report today
        assert len(reports) == 1
        report = reports[0]
        dct = report.get_dictionary()
        assert report.weight == 5.2
        assert report.height == 95.5
        assert report.stunted == False
        assert report.weight_for_height == "60%-"
        
    def test_03_message_log(self):
        failures = MessageLog.objects.filter(form_error=True).count()
        # testing for every failure is a pain, there should be some is probably enough
        assert failures, "Got no failures in the MessageLog"

    test_04_exiting = """
        1234567 > NEW 70 1201 F 26082005 9999999
        1234567 < You have attempted to register child #70 in Salima GMC. However, this child already exists. If this is an error, please resend SMS with correct information. If this patient is new or a replacement, please use the EXIT command first, then re-register.

        1234567 > EXIT 32 1201
        1234567 < No reason given must be one of: D (death), DM (death malnutrition), DO (dropout), M (mistake).

        1234567 > EXIT 70 1201 DM
        1234567 < Thank you for informing us that Child #70 cancelled for at Salima GMC #1201 has exited program. Reason given: death of causes related to malnutrition.
        
        1234567 > NEW 70 1201 F 26082005 9999999
        1234567 < Thank you for registering child #70 in Salima GMC, female, age 46 months, born 26.08.2005, contact# 9999999. If there is a mistake, please use EXIT to cancel this registration and try again.
        
        # need to check this goes on the new child
        1234567 > REPORT 70 5.2 95.5 13.5 N Y
        1234567 < Thank you Mariam Coulibaly for reporting child #70, weight = 5.2 kg, height = 95.5 cm, MUAC = 13.5 cm, no oedema, yes diarrhea. This child has severe acute malnutrition. Please refer to a clinician immediately for admission into the NRU/TFP.
    """
    
    def test_04_exiting_test(self):
        """ Test that as a result of this, we have two seperate cases with their own reports """
        case = Case.objects.filter(ref_id=70).order_by("id")
        assert case[0].active == False
        assert case[1].active == True
        assert case[0].reportmalnutrition_set.latest().muac == 127
        assert case[1].reportmalnutrition_set.latest().muac == 135
        
    test_05_cancelling = """
        1234567 > REPORT 70 25.2 95.5 13.5 N Y
        1234567 < Thank you Mariam Coulibaly for reporting child #70, weight = 25.2 kg, height = 95.5 cm, MUAC = 13.5 cm, no oedema, yes diarrhea. This child is healthy. Please thank the caregiver and remind her/him to return next month. If these measurements are not correct, please resend a corrected report immediately.
        
        1234567 > CANCEL 70
        1234567 < Last report for 70 cancelled
        
        1234567 > CANCEL 70
        1234567 < No report for 70 to cancel
        
        1234567 > REPORT 70 5.2 95.5 13.5 N Y
        1234567 < Thank you Mariam Coulibaly for reporting child #70, weight = 5.2 kg, height = 95.5 cm, MUAC = 13.5 cm, no oedema, yes diarrhea. This child has severe acute malnutrition. Please refer to a clinician immediately for admission into the NRU/TFP.
    """
    
    def test_05_post_setup(self):
        case = Case.objects.get(ref_id=70, active=True)
        report = case.reportmalnutrition_set.latest()
        # move it back in time
        report.entered_at = report.entered_at - timedelta(days=50)
        report.save()
    
    test_06_diarrhea = """
        1234567 > REPORT 70 5.2 95.5 13.5 N Y
        1234567 < Thank you Mariam Coulibaly for reporting child #70, weight = 5.2 kg, height = 95.5 cm, MUAC = 13.5 cm, no oedema, yes diarrhea. This child has severe acute malnutrition. Please refer to a clinician immediately for admission into the NRU/TFP. This child also has persistent diarrhea.
    """
    
    test_07_help = """
        1234567 > help
        1234567 < To register yourself, SMS the following:  JOIN LastName FirstName Username To register a child, SMS the following:  NEW Child# GMC# gender DOB contact# To record information on an existing child, SMS the following:  Child# GMC# weight height muac oedema diarrhea
    """