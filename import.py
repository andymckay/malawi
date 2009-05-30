import csv
import os

os.environ["RAPIDSMS_INI"] = "rapidsms.ini"
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

import sys
sys.path.append("..")

from rapidsms.config import Config
from rapidsms.manager import Manager
from django.core.management import execute_manager, setup_environ

conf = Config(os.environ["RAPIDSMS_INI"])

import settings
setup_environ(settings)

from malnutrition.sms.resolve import models
from apps.sms.models.base import Case, Provider
from datetime import datetime
import time

reader = csv.reader(open('migration/data/migrate-reporter.csv', 'r'))
for row in reader: 
    user = models.User()
    user.username = str("%s-%s" % (time.time(), row[0]))
    user.save()
    provider = Provider()
    provider.id = row[0]
    provider.mobile = row[1]
    provider.user = user
    provider.save()

reader = csv.reader(open('migration/data/migrate-rawmessages.csv', 'r'))
for row in reader:
    mlog = models.MessageLog()
    provider = Provider.objects.get(id=int(row[0]))
    user = provider.user
    mlog.mobile = provider.mobile
    mlog.user = user
    mlog.text = row[1]
    mlog.save()
    mlog.created_at = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
    mlog.save()

reader = csv.reader(open('migration/data/migrate-children.csv', 'r'))
for row in reader:
    fac = models.Facility.objects.get(id=65)
    if row[1]:
        dob = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S").date()
        case = Case()
        case.gender = row[2].upper()
        case.ref_id = int(row[0])
        case.dob = dob
        case.mobile = row[3]
        provider = Provider.objects.get(id=int(row[4]))
        case.provider = provider
        # since there's only one clinic
        provider.clinic = fac
        provider.save()
        #case.village = models.Facility.objects.get(id=65) # this is the only one we have 
        case.facility = fac
        case.zone = models.Zone.objects.get(id=44)
        case.save()
    else:
        print "Ignoring due to bad date", row[0]


reader = csv.reader(open('migration/data/migrate-reports.csv', 'r'))
for row in reader:
    report = models.ReportMalnutrition()
    report.provider = models.Provider.objects.get(id=int(row[0]))
    try:
        report.case = models.Case.objects.get(ref_id=int(row[1]))
    except models.Case.DoesNotExist:
        continue
    report.weight = float(row[2])
    report.height = float(row[3])
    if row[4]:
        report.muac = int(float(row[4]) * 10)
    report.save()
    report.entered_at = datetime.strptime(row[7], "%Y-%m-%d %H:%M:%S")
    if str(row[5]) == "1":
        report.observed.add(models.Observation.objects.get(uid="oedema"))
    if str(row[6]) == "1":
        report.observed.add(models.Observation.objects.get(uid="diarrhea"))
    report.save()