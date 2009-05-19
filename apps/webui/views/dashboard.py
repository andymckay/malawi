from apps.sms.models.base import ReportMalnutrition, Zone, Provider, Facility
from malnutrition.ui.views.shortcuts import as_html
from malnutrition.utils.graph import Graphs

from django.db.models import Q
from django.core.cache import cache
 
import csv
import StringIO
from datetime import datetime
from django.http import HttpResponse

from apps.webui.forms.filter import FilterForm

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
def _zones(method, limit, zones, *args):
    data = []
    for area in Zone.objects.filter(zones):
        providers = providers_by_zone(area.id, *args)
        res = []
        if providers:
            if limit:
                res = method("AND provider_id in (%s)" % (limit, ",".join(providers)), 365, *args)
            else:
                res = method("AND provider_id in (%s)" % ",".join(providers), 365, *args)
        data.append({ "name": area.name, "data": res })
    return data

def zones_plus_total(method, limit, zones, *args):
    """ How do we break down the reports by zone? """
    data = [ { "name": "All", "data": method(limit, 365, *args) }, ]
    data += _zones(method, limit, zones, *args)
    return data
    
def zones(method, limit, zones, *args):
    return _zones(method, limit, zones, *args)



def view(request):
    context = {}
    
    limit = None
    filter = request.GET.get("zone", None)
    try:
        filter = int(filter)
    except (TypeError, AttributeError, ValueError):
        pass
        
    if not filter:
        method = zones_plus_total
        qfilter = Q(category=4)
    else:
        method = zones
        qfilter = Q(id=filter)
    
    graphs = Graphs(
        classes={ "ReportMalnutrition": ReportMalnutrition, "Zone": Zone }, 
        zone_lookup = method, 
        zones = qfilter,
        limit = limit
        )
    context["message"] = graphs.render(name="message", type=graphs.count, args=None)
    context["severe"] = graphs.render(name="severe", type=graphs.percentage_status, args=[2,3])
    context["moderate"] = graphs.render(name="moderate", type=graphs.percentage_status, args=[1,])
    context["oedema"] = graphs.render(name="oedema", type=graphs.percentage_observation, args=12)
    context["diarrhea"] = graphs.render(name="diarrhea", type=graphs.percentage_observation, args=2)
    context["muac"] = graphs.render(name="muac", type=graphs.average, args="muac")
    context["weight"] = graphs.render(name="weight", type=graphs.average, args="weight")
    context["height"] = graphs.render(name="height", type=graphs.average, args="height")
    context["stunting"] = graphs.render(name="stunting", type=graphs.percentage_stunting, args=None)
    
    export = request.GET.get("export", None)
    if export:
        data = context.get(export, None)
        output = StringIO.StringIO()
        csvio = csv.writer(output)
        header = False
        for row in data.data:
            if not header:
                csvrow = [export,] + ([datetime.fromtimestamp(float(f[0])/1000).date() for f in row["data"]])
                csvio.writerow(csvrow)
                header = True

            csvrow = [row["name"], ] + [f[1] for f in row["data"]]
            csvio.writerow(csvrow)
            
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=report.csv'    
        response.write(output.getvalue())
        return response
    
    lastmonth = []
    lastmonthdata = {}

    # bit complicated, but will give us the last month data by inspecting the graphs
    for k, v in context.items():
        if v and not isinstance(v, dict):
            for region in v.data:
                key = region["name"]
                if not lastmonthdata.has_key(key):
                    lastmonthdata[key] = {}

                if region["data"]:
                    lastmonthdata[key][k] = region["data"][-1][1]

    context["lastmonth"] = lastmonthdata.items()
    context["lastmonth"].sort()
    
    form = FilterForm(request.GET)
    zone_list = [ [z.id, z.name ] for z in Zone.objects.filter(Q(category=4)) ]
    zone_list = [ ["", "All"], ] + zone_list
    form.fields["zone"].choices = zone_list
    context["filter"] = form
    
    return as_html(request, "dashboard.html", context)
    