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
    
    # if this is a zone that has children, go find them
    zones = [zone,]
    if hasattr(zone, "children"):
        children = zone.children()
        if children:
            zones = children
    
    # so have we got facilities, or do we need to go looking for them?
    if not isinstance(zones[0], Facility):
        zones = [ str(p["id"]) for p in Facility.objects.filter(zone__in=zones).values("id").distinct()]

    # finally get some providers
    providers = Provider.objects.filter(clinic__in=zones).values("id").distinct()
    result = [ str(p["id"]) for p in providers ]
    cache.set("providers_by_zone_%s" % zone, result, 60)
    return result

# so in malawi, all is everyone
# and the rest is category 4, this will be slightly different in Kenya
def _zones(method, limit, root, zones, facilities, *args):
    data = []
    # start with the root
    if root:
        providers = providers_by_zone(root, *args)
        data.append({ "name": "All (%s)" % root.name, "data": method("AND provider_id in (%s)"  % (",".join(providers)), 365, *args)})
    else:
        data.append({ "name": "All (National)", "data": method("", 365, *args)})

    # then do the zones
    _zones = Zone.objects.filter(zones)
    if not _zones:
        _zones = Facility.objects.filter(facilities)

    for area in _zones:
        providers = providers_by_zone(area, *args)
        res = []
        if providers:
            if limit:
                res = method("%s AND provider_id in (%s)" % (limit, ",".join(providers)), 365, *args)
            else:
                res = method("AND provider_id in (%s)" % ",".join(providers), 365, *args)
        data.append({ "name": area.name, "data": res })
    return data

def zones_plus_total(method, limit, root, zones, facilities, *args):
    """ How do we break down the reports by zone? """
    return _zones(method, limit, root, zones, facilities, *args)

def _view(request, root, zones, facilities):
    context = {}

    graphs = Graphs(
        classes={ "ReportMalnutrition": ReportMalnutrition, "Zone": Zone }, 
        zone_lookup = zones_plus_total, 
        zones = zones,
        root = root,
        limit = "",
        facilities = facilities
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
    
    # we want the zones for the table, but don't want to filter down onto a village (or GMC)
    # maybe, not sure
    _zones_filter = Zone.objects.filter(zones).order_by("name")
    _zones_list = _zones_filter
    if not _zones_list:
        _zones_list = Facility.objects.filter(facilities).order_by("name")
        
    
    form = FilterForm(request.GET)
    zone_list = [ [z.id, z.name ] for z in _zones_list ]
    zone_list = [ ["", "All"], ] + zone_list
    form.fields["zone"].choices = zone_list
    context["filter"] = form
    context["zones"] = _zones_filter

    current = root
    context["breadcrumbs"] = [
    { "link": "/", "title":"National"},
    ]
    if root:
        while current.parent():
            current = current.parent()
            context["breadcrumbs"].append({"link": "/zone/%s/" % current.id, "title": current.name })
        context["breadcrumbs"].append({"link": "/zone/%s/" % root.id, "title": root.name }) 
        
    return as_html(request, "dashboard.html", context)

def view(request, zone_id=None):
    if not zone_id:
        # we are at the root
        root = None
        zones = Q(category=4)
        facilities = None
    else:
        zone = Zone.objects.get(id=zone_id)
        root = zone
        zones = Q(head=zone)
        facilities = Q(zone=zone)
    return _view(request, root, zones, facilities) 