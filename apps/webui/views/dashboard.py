import csv
import StringIO
from datetime import datetime

from django.http import HttpResponse
from django.db.models import Q
from django.core.cache import cache

from apps.sms.models.base import ReportMalnutrition, Zone, Provider, Facility
from apps.webui.forms.filter import FilterForm
from apps.shortcuts import has_access, has_roles

from malnutrition.ui.views.shortcuts import as_html
from malnutrition.utils.graph import Graphs
from django.contrib.auth.decorators import login_required

# WARNING this is far too complicated and I have plan to simplify this
# a lot! Here be dragons!
# 
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
    _zones = []
    if zones:
        _zones = Zone.objects.filter(zones)
    if not _zones and facilities:
        _zones = Facility.objects.filter(facilities)

    if len(_zones) > 1:
        if root:
            providers = providers_by_zone(root, *args)
            data.append({ "name": "All (%s)" % root.name, "data": method("AND provider_id in (%s)"  % (",".join(providers)), 365, *args)})
        else:
            data.append({ "name": "All (National)", "data": method("", 365, *args)})

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

def _facilities(method, facilities, *args):
    #import pdb; pdb.set_trace()
    facility = Facility.objects.filter(facilities)[0]
    
    data = []
    providers = Provider.objects.filter(clinic=facility.id).values("id").distinct()
    result = [ str(p["id"]) for p in providers ]
    
    #print result
    if result:
        res = method("AND provider_id in (%s)" % ",".join(result), 365, *args)
        data.append({ "name": facility.name, "data": res })
    return data 
    
def zones_plus_total(method, limit, root, zones, facilities, *args):
    """ How do we break down the reports by zone? """
    return _zones(method, limit, root, zones, facilities, *args)

def facilities_lookup(method, limit, root, zones, facilities, *args):
    #import pdb; pdb.set_trace()
    return _facilities(method, facilities, *args)

def _view(request, graphs, root, zones_all, facilities_all):
    context = {}

    context["message"] = graphs.render(name="message", type=graphs.count, args=None)
    context["severe"] = graphs.render(name="severe", type=graphs.percentage_status, args=[2,3])
    context["moderate"] = graphs.render(name="moderate", type=graphs.percentage_status, args=[1,])
    context["oedema"] = graphs.render(name="oedema", type=graphs.percentage_observation, args=1)
    context["diarrhea"] = graphs.render(name="diarrhea", type=graphs.percentage_observation, args=3)
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
    _zones_filter = _zones_list = _facilities_list = _facility_filter = []
    if zones_all:
        _zones_filter = _zones_list = Zone.objects.filter(zones_all).order_by("name")
    if facilities_all:
        _facilities_list = _facility_filter = Facility.objects.filter(facilities_all).order_by("name")
    
    form = FilterForm(request.GET)
    zone_list = [ [z.id, z.name ] for z in _zones_list ]
    zone_list = [ ["", "All"], ] + zone_list
    form.fields["zone"].choices = zone_list
    context["filter"] = form
    context["zones"] = _zones_filter

    context["facilities"] = _facility_filter

    current = root
    context["breadcrumbs"] = [
    { "link": "/", "title":"National"},
    ]
    if root and hasattr(root, "parent"):
        while current.parent():
            current = current.parent()
            context["breadcrumbs"].insert(1, {"link": "/zone/%s/" % current.id, "title": current.name })
        context["breadcrumbs"].append({"link": "/zone/%s/" % root.id, "title": root.name }) 

    return as_html(request, "dashboard.html", context)

@login_required
def view(request, zone_id=None, facility_id=None):
    dct = {
        "classes": { "ReportMalnutrition": ReportMalnutrition, "Zone": Zone },
        "limit": "",
    }
    access = False
    
    if not zone_id and not facility_id:
        access = has_access(request)
        if not access:
            # according to the docs, district has access to the national page
            access = has_roles(request.user, ["district",])
            
        # we are at the root
        zone = None
        root = None
        zones = Q(category=4)
        facilities = None
        zones_all = Q(category=4)
        facilities_all = facilities
        zone_lookup = zones_plus_total
    elif facility_id:
        zone = Facility.objects.get(id=facility_id)
        access = has_access(request, facility=zone)
        
        root = zone
        zones = None
        facilities = Q(id=facility_id)
        zones_all = None
        facilities_all = None
        zone_lookup = facilities_lookup
    elif zone_id:
        zone = Zone.objects.get(id=zone_id)
        access = has_access(request, zone=zone)
        
        root = zone
        zones = Q(head=zone)
        facilities = Q(zone=zone)
        zones_all = zones
        facilities_all = facilities
        zone_lookup = zones_plus_total
    
    filter_zone = request.GET.get("filter_zone")

    if filter_zone:
        zones = Q(id=filter_zone)
    

    dct["zones"] = zones
    dct["zone_lookup"] = zone_lookup
    dct["root"] = root
    dct["facilities"] = facilities

    graphs = Graphs(**dct)
    if access:
        return _view(request, graphs, root, zones_all, facilities_all) 
    else:
        return as_html(request, "no_access.html", {})