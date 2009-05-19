# -*- coding: utf-8 -*-
from rapidsms.tests.scripted import TestScript
from django.core.management import call_command
from django.test import TestCase
from datetime import datetime
from app import App

from apps.sms.models.base import ReportMalnutrition, Case

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
        
        1234567 > JOIN 1201 Andy McKay 
        1234567 < An existing user Coulibaly Mariam at GMC #1201 is already registered to this phone number.  Confirm registration by replying N (for no) or Y (for yes).
        
        # to do, complete this
    """
    
    test_01_registration = """
        # test registration
        1234568 > NEW 69 1201 M 19102008 09555123
        1234568 < 1234568 is not a registered number.
        
        1234567 > NEW 69 1201 M 19102008
        1234567 < You have attempted to register child #69 in Salima GMC.  However, this child already exists.  If this is an error, please resend SMS with correct information. Please this child is a replacement, please confirm registration replying D (previous child died) or R (previous child replaced in program).
        
        1234567 > NEW 69 1201 M 19102008 123124124
        1234567 < You have attempted to register child #69 in Salima GMC.  However, this child already exists.  If this is an error, please resend SMS with correct information. Please this child is a replacement, please confirm registration replying D (previous child died) or R (previous child replaced in program).

        1234567 > NEW 70 1201 M 19102008 123124124
        1234567 < Thank you for registering child #70 in Salima GMC, male, age %s months, born 19.10.2008, contact# 123124124. If there is a mistake, please cancel this registration and try again.
        
        1234567 > NEW 70 1201 M 19102003 123124124
        1234567 < You have attempted to register child #70. However, the date of birth entered is 10.19.2003. The age of this child is above 5 years. Please resend SMS with corrected age.
        
        #1234567 > NEW 69 1201 cancel
        #1234567 < foo
    """ % (years_months("19/10/2008")[1])
    
    test_02_report = """
        # test reporting
        1234567 > REPORT 68 25.2 95.5 8.3 N Y
        1234567 < That child is not registered.
        
        1234567 > REPORT 70 Foo 95.5 8.3 N Y
        1234567 < Thank you for reporting that child. The weight entered is in error. Please correct the weight and resend a corrected report immediately.

        1234567 > REPORT 70 Foo 95.5 8.3 
        1234567 < Thank you for reporting that child. The weight entered is in error. Please correct the weight and resend a corrected report immediately. The oedema entered is in error. Please correct the oedema and resend a corrected report immediately. The diarrhea entered is in error. Please correct the diarrhea and resend a corrected report immediately.
        
        1234568 > REPORT 70 25.2 95.5 130 N Y
        1234568 < 1234568 is not a registered number.
        
        1234567 > REPORT 70 25.2 95.5 130 N Y
        1234567 < Thank you Mariam Coulibaly for reporting child #70, weight = 25.2, height = 95.5, MUAC = 130.0, no oedema, yes diarrhea. This child is healthy. Please thank the caregiver and remind her/him to return next month. If these measurements are not correct, please resend a corrected report immediately.

        1234567 > REPORT 70 25.2 95.5 120 N Y
        1234567 < Thank you Mariam Coulibaly for reporting child #70, weight = 25.2, height = 95.5, MUAC = 120.0, no oedema, yes diarrhea. This child has moderate acute malnutrition. Please refer to Supplementary Feeding Programme (SFP) and counsel caregiver on child nutrition.
                
        1234567 > REPORT 70 25.2 95.5 100 N Y
        1234567 < Thank you Mariam Coulibaly for reporting child #70, weight = 25.2, height = 95.5, MUAC = 100.0, no oedema, yes diarrhea. This child has severe acute malnutrition. Please refer to a clinician immediately for admission into the NRU/TFP.
    """
    
    def test_02_report_test(self):
        case = Case.objects.get(ref_id=70)
        reports = ReportMalnutrition.objects.filter(case=case)
        # we keep deleting so we only have report today
        assert len(reports) == 1
        report = reports[0]
        dct = report.get_dictionary()
        assert report.weight == 25.2
        assert report.height == 95.5
        assert report.stunted == False
        assert report.weight_for_height == "100%-85%"