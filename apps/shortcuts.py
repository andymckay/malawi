from datetime import date, datetime, timedelta
from django.db.models import ObjectDoesNotExist

DEBUG = False
DEBUG = True

from apps.sms.models.base import Provider


def log(msg):
    return 
    if DEBUG:
        print msg

def get_providers(user):
    try:
        profile = user.get_profile()
    except ObjectDoesNotExist:
        log("No profile, no access")
        return False 
        
    if profile.facility:
        return [ p.id for p in Provider.objects.filter(clinic=profile.facility) ]
    
    if profile.zone:
        from apps.webui.views.dashboard import providers_by_zone
        return providers_by_zone(profile.zone)
        
def has_roles(user, roles=[]):
    # for use in the user_passes_test_decorator
    if user.is_superuser or user.is_staff:
        log("Superuser, full access")
        return True

    try:
        profile = user.get_profile()
    except ObjectDoesNotExist:
        log("No profile, no access")
        return False
    
            
    for role in roles:
        if isinstance(role, str):
            role = getattr(profile, role.upper(), None)
        if int(profile.role) == role:
            log("Matched up role %s, access" % role)
            return True
        
    return False

def has_access(request, zone=None, facility=None):
    """ Given a request (and hence a user), what do they have access to? """
    
    if request.user.is_superuser:
        log("Superuser, full access")
        return True
        
    if request.user.is_staff:
         # since they have admin access anyway
         log("Staff, full access")
         return True
        
    try:
        profile = request.user.get_profile()
    except ObjectDoesNotExist:
        log("No profile, no access")
        return False
    
    # national and partner have pretty much access to everything
    if int(profile.role) in [profile.NATIONAL, profile.PARTNER]:
        log("National or Partner, access")
        return True
    
    # gmc just to the facility only
    if int(profile.role) == profile.GMC:
        log("GMC user")
        if facility and profile.facility == facility:
            log("Facility match, access")
            return True
    
    # district, zone and facility only
    if int(profile.role) == profile.DISTRICT:
        log("District user")
        if zone and profile.zone == zone:
            log("Zone match, access")
            return True
        if zone and profile.zone == zone.parent():
            log("Zone parent match, access")
            return True
        if facility and profile.zone in [facility.parent(), facility.parent().parent()]:
            log("Facility parent match, access")
            return True
    
    log("Fall back at the end, denied.")
    return False
    

def parser(text):
    """ This is the text format requested, which unfortunately strptime doesn't understand """
    return date(year=int(text[4:8]),day=int(text[0:2]),month=int(text[2:4]))
    
def last_month():
    now = datetime.now()
    previous = now - timedelta(days=now.day)
    beginning = datetime(year=previous.year, month=previous.month, day=1)
    end = datetime(year=previous.year, month=previous.month, day=previous.day)
    return beginning, end

def this_month():
    now = datetime.now()
    beginning = datetime(year=now.year, month=now.month, day=1)
    end = datetime(year=now.year, month=now.month, day=now.day)
    return beginning, end

if __name__=="__main__":
    print last_month()