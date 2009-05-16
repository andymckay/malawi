# -*- coding: utf-8 -*-
from rapidsms.tests.scripted import TestScript
from django.core.management import call_command
from django.test import TestCase
from datetime import datetime
from app import App

def years_months(dt):
    dt = datetime.strptime(dt, "%d/%m/%Y").date()
    now = datetime.now().date()
    ymonths = (now.year - dt.year) * 12
    months = ymonths + (now.month - dt.month)
    return (now.year - dt.year, months)
    
loaded = False
class TestApp (TestScript):
    apps = (App,)
    fixtures = ("base.json", "auth.json")
    
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
        1234567 > JOIN Coulibaly Mariam 1202
        1234567 < The GMC ID given does not exist.
        
        1234567 > JOIN Coulibaly Mariam 1201
        1234567 < Name = Coulibaly Mariam, GMC = Salima 1201, Phone number = 1234567. If this is not correct, please re-register.
        
        1234567 > JOIN Andy McKay 1201
        1234567 < An existing user Coulibaly Mariam at GMC #1201 is already registered to this phone number.  Confirm registration by replying N (for no) or Y (for yes).
        
        # to do, complete this
    """
    
    test_01_registration = """
        # test registration
        1234568 > NEW 69 1201 M 19102008 09555123
        1234568 < 1234568 is not a registered number.
        
        1234567 > NEW 69 1201 M 19102008
        1234567 < That child already exists.
        
        1234567 > NEW 69 1201 M 19102008 123124124
        1234567 < That child already exists.

        1234567 > NEW 70 1201 M 19102008 123124124
        1234567 < Thank you for registering child #70 in Salima GMC, male, age %s months, born 19.10.2008, contact# 123124124. If there is a mistake, please cancel this registration and try again.
        
        1234567 > NEW 70 1201 M 19102008 123124124
        1234567 < That child already exists.
    """ % (years_months("19/10/2008")[1])