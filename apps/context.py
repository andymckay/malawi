from django.conf import settings
from apps.shortcuts import has_roles

def processor(self):
    user = self.user
    tabs = []
    if has_roles(user, ["partner", "national", "district"]):
        tabs.append({ "link": "/", "title": "National" })
        tabs.append({ "link": "/district/", "title": "District"})
    if has_roles(user, ["partner", "national", "district", "gmc"]):
        tabs.append({ "link": "/gmc/", "title": "GMC"})
        tabs.append({ "link": "/child/", "title": "Child"})
        tabs.append({ "link": "/hsa/", "title": "HSA"})
    if has_roles(user, ["partner", "national", "district"]):
        tabs.append({ "link": "/setup/", "title": "Setup"})
    tabs.append({ "link": "/background/", "title": "Background"})
    context = {
        "site": { "title": "Malawi",
                  "tabs": tabs },
        "settings": settings,
    }
    return context