from django.db import connection
from apps.sms.models.base import ReportMalnutrition, Zone, Provider, Facility
from malnutrition.ui.views.shortcuts import as_html
from malnutrition.utils.graph import Graphs

from django.core.cache import cache

# zones vary by project
def providers_by_zone(zone, *args):
    """ To find a message per region we need to go
        provider > facility > zone > zone etc... until 
        we find the key zone.
    
        This is Malawi specific for now

        """
    cached = cache.get("providers_by_zone_%s" % zone)
    if cached:
        return cached
    
    root = Zone.objects.get(id=zone)
    sub = Zone.objects.filter(head=zone).values("id").distinct()
    facilities = Facility.objects.filter(zone__in=sub).values("id").distinct()
    providers = Provider.objects.filter(clinic__in=facilities).values("id").distinct()
    result = [ str(p["id"]) for p in providers ]
    cache.set("providers_by_zone_%s" % zone, result, 60)
    return result

# so in malawi, all is everyone
# and the rest is category 4, this will be slightly different in Kenya
def reports_by_zone(method, limit, *args):
    """ How do we break down the reports by zone? """
    data = [ { "name": "All", "data": method(limit, 365, *args) }, ]
    for area in Zone.objects.filter(category=4):
        providers = providers_by_zone(area.id, *args)
        res = []
        if providers:
            if limit:
                res = method("AND provider_id in (%s)" % (limit, ",".join(providers)), 365, *args)
            else:
                res = method("AND provider_id in (%s)" % ",".join(providers), 365, *args)
        data.append({ "name": area.name, "data": res })
    return data

def view(request):
    context = {}
    
    graphs = Graphs(classes={ "ReportMalnutrition": ReportMalnutrition, "Zone": Zone }, zone_lookup=providers_by_zone)
    context["message"] = graphs.render(name="message", by_zone=reports_by_zone, type=graphs.count, limit=None, args=None)
    context["severe"] = graphs.render(name="severe", by_zone=reports_by_zone, type=graphs.percentage_status, limit=None, args=[2,3])
    context["moderate"] = graphs.render(name="moderate", by_zone=reports_by_zone, type=graphs.percentage_status, limit=None, args=[1,])
    context["oedema"] = graphs.render(name="oedema", by_zone=reports_by_zone, type=graphs.percentage_observation, limit=None, args=12)
    context["diarrhea"] = graphs.render(name="diarrhea", by_zone=reports_by_zone, type=graphs.percentage_observation, limit=None, args=2)
    context["muac"] = graphs.render(name="muac", by_zone=reports_by_zone, type=graphs.average, limit=None, args="muac")
    context["weight"] = graphs.render(name="weight", by_zone=reports_by_zone, type=graphs.average, limit=None, args="weight")
    context["height"] = graphs.render(name="height", by_zone=reports_by_zone, type=graphs.average, limit=None, args="height")
    
    return as_html(request, "dashboard.html", context)
    