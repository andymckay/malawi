import csv
import StringIO
from datetime import datetime

from django.http import HttpResponse
from django.db.models import Q
from django.core.cache import cache

from apps.sms.models.base import ReportMalnutrition, Zone, Provider, Facility, Case
from apps.webui.forms.filter import FilterForm
from apps.shortcuts import has_access, has_roles

from malnutrition.ui.views.shortcuts import as_html
from malnutrition.utils.graph import Graphs
from django.contrib.auth.decorators import login_required

def _zones(self):
    # this method, given a zone, sets up the sql appropriately for all the zones
    our_zones = Zone.objects.filter(self.zones)
    data = []
    ids = []     
    for zone in our_zones:
        zones = zone.get_child_ids() + [str(zone.id),]
        ids.append(str(zone.id))
        if self.zones:
            if self.limit:
                data.append({ "name": zone.name, "limit": "%s AND zone_id in (%s)" % (self.limit, ",".join(zones)) })
            else:
                data.append({ "name": zone.name, "limit": "AND zone_id in (%s)" % ",".join(zones) })
            
    if len(ids) > 1:
        if self.root:
            data.insert(0, { "name": "All (%s)" % self.root.name, "limit": "AND zone_id in (%s)"  % (",".join(ids))})
        else:
            data.insert(0, { "name": "All (National)", "limit": "" })
    
    return data 

def _facilities(self):
    # this sets up all the facility
    facilities = Facility.objects.filter(self.facilities)
    data = []
    ids = []
    
    for facility in facilities:
        ids.append(str(facility.id))
        data.append({ "name": facility.name, "limit": "AND facility_id = %s" % facility.id},)
    
    if len(ids) > 1:
        data.insert(0, { "name": "All (%s)" % self.root.name, "limit": "AND facility_id in (%s)"  % (",".join(ids))})

    return data

def _view(request, graphs, root):
    """ Assemble the graphs and bits the user wants """
    context = {}

    context["message"] = graphs.render(name="message", type=graphs.count, args=[])
    context["severe"] = graphs.render(name="severe", type=graphs.percentage_status, args=[2,3])
    context["moderate"] = graphs.render(name="moderate", type=graphs.percentage_status, args=[1,])
    context["oedema"] = graphs.render(name="oedema", type=graphs.percentage_observation, args=[1,])
    context["diarrhea"] = graphs.render(name="diarrhea", type=graphs.percentage_observation, args=[3,])
    context["muac"] = graphs.render(name="muac", type=graphs.average, args=["muac",])
    context["weight"] = graphs.render(name="weight", type=graphs.average, args=["weight",])
    context["height"] = graphs.render(name="height", type=graphs.average, args=["height",])
    context["stunting"] = graphs.render(name="stunting", type=graphs.percentage_stunting, args=[])
    
    export = request.GET.get("export", None)
    if export:
        return _csv_export(context, export)
    

    context["lastmonth"] = _setup_last_month(context)
    context["filter"], context["zones"] = _setup_zones_filter(request, graphs.zones_unfiltered)
    context["facilities"] = _setup_facility_filter(graphs.facilities)
    context["breadcrumbs"] = _add_breadcrumbs(root)
    return as_html(request, "dashboard.html", context)

def _csv_export(context, export):
    """ Did the user ask for a csv export? if so.... """
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

def _setup_last_month(context):
    """ Given the graphs, set up the table of the last month data """
    lastmonthdata = {}
    lastmonth = []
    # bit complicated, but will give us the last month data by inspecting the graphs
    for k, v in context.items():
        if v and not isinstance(v, dict):
            for region in v.data:
                key = region["name"]
                if not lastmonthdata.has_key(key):
                    lastmonthdata[key] = {}

                if region["data"]:
                    lastmonthdata[key][k] = region["data"][-1][1]

    lastmonth = list(lastmonthdata.items())
    lastmonth.sort()

    return lastmonth

def _setup_zones_filter(request, zones):
    """ This sets up the zones for the right hand side """
    if zones:
        _zones_filter = _zones_list = Zone.objects.filter(zones).order_by("name")
        form = FilterForm(request.GET)
        zone_list = [ [z.id, z.name ] for z in _zones_list ]
        zone_list = [ ["", "All"], ] + zone_list
        form.fields["zone"].choices = zone_list
        return form, _zones_filter
    else:
        return None, []

def _setup_facility_filter(facilities):
    """ This sets up the facilities for the right hand side """
    if facilities:
        return Facility.objects.filter(facilities).order_by("name")
    return []
    
def _add_breadcrumbs(root):
    """ This does the breadcrumbs for the top of the page """
    current = root
    breadcrumbs = [
        { "link": "/", "title":"National"},
    ]
    if root and hasattr(root, "parent"):
        while current.parent():
            current = current.parent()
            breadcrumbs.insert(1, {"link": "/zone/%s/" % current.id, "title": current.name })
        breadcrumbs.append({"link": "/zone/%s/" % root.id, "title": root.name })
    return breadcrumbs

@login_required
def view(request, zone_id=None, facility_id=None):
    """ This is the main view that is a pretty magic view
    it figures out if you are looking for a facility, a zone
    or none at all. It then sets up the graph and passess on
    to a view to do the real work"""
    dct = {
        "classes": { "ReportMalnutrition": ReportMalnutrition, "Zone": Zone, "Case": Case },
        "limit": "",
    }
    access = False
    
    if not zone_id and not facility_id:
        # right so here are at the root of the site
        access = has_access(request)
        if not access:
            # according to the docs, district has access to the national page
            access = has_roles(request.user, ["district",])
            
        # we are at the root, so we set the root to non
        root = None
        # this is malawi specific, give us the districts
        zones = Q(category=4)
        facilities = None
        # to setup the SQL, use the _zones method
        sql_setup = _zones
    elif facility_id:
        # here we are looking at a facility
        root = Facility.objects.get(id=facility_id)
        access = has_access(request, facility=root)
        
        zones = None
        facilities = Q(id=facility_id)
        # use the right sql method for the setup
        sql_setup = _facilities
    elif zone_id:
        # this gets a little more complicated
        # because the sub zones could be zones or facilites
        root = Zone.objects.get(id=zone_id)
        access = has_access(request, zone=root)
        facilities = Q(zone=root)
        if not root.get_child_ids():
            # then we need to look for facilities
            sql_setup = _facilities
        else:
            sql_setup = _zones
            
        zones = Q(head=root)

    # do we need to filter
    filter_zone = request.GET.get("filter_zone")

    # this is used to show the filters on the right of the screen
    dct["zones_unfiltered"] = zones

    if filter_zone:
        zones = Q(id=filter_zone)
    
    dct["zones"] = zones
    dct["sql_setup"] = sql_setup
    dct["root"] = root
    dct["facilities"] = facilities

    graphs = Graphs(**dct)
    if access:
        return _view(request, graphs, root) 
    else:
        return as_html(request, "no_access.html", {})