from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q

from reusable_table.table import get_dict, get

from malnutrition.ui.views.shortcuts import as_html

from apps.sms.models.base import Case, Zone, Facility
from apps.shortcuts import has_access, has_roles, get_providers

@login_required
def hsa(request):
    q = Q()
    if not has_roles(request.user, "partner"):
        q = Q(id__in=get_providers(request.user))
    nonhtml, tables = get_dict(request, [
        ["providers", q],
    ])
    if nonhtml:
        return nonhtml

    context = {}
    context.update(tables)

    return as_html(request, "hsa.html", context)

@login_required
def district(request):
    districts = []
    for district in Zone.objects.filter(category=5).order_by("name"):
        if has_access(request, zone=district):
            districts.append(district)
            
    return as_html(request, "district.html", {"districts": districts})

@login_required
def gmc(request):
    gmcs = []
    for gmc in Facility.objects.filter().order_by("name"):
        if has_access(request, facility=gmc):
            gmcs.append(gmc)

    return as_html(request, "gmc.html", {"facilities": gmcs})

@login_required
def child_list(request):
    q = Q()
    if not has_roles(request.user, "partner"):
        q = Q(provider__in=get_providers(request.user))

    nonhtml, tables = get(request, [
        ["case", q & Q(active=True)],
        ["reports", q],
        ["case", q & Q(active=False)]
    ])
    if nonhtml:
        return nonhtml

    context = {}
    context["active"] = tables[0]
    context["reports"] = tables[1]
    context["inactive"] = tables[2]

    return as_html(request, "child_list.html", context)
    
@login_required
@user_passes_test(lambda u: u.is_staff )
def setup(request):
    nonhtml, tables = get(request, [
        ["facilities", Q()],
        ["zones", Q(category=5)],
        ["zones", Q(category=4)],
        ["message", Q(form_error=False)],
        ["message", Q(form_error=True)],
    ])
    if nonhtml:
        return nonhtml

    context = {
        "facilities": tables[0],
        "regions": tables[1],
        "districts": tables[2],
        "message_pass": tables[3],
        "message_fail": tables[4]
    }

    return as_html(request, "setup.html", context)
    
@login_required
def child_view(request, object_id):
    case = Case.objects.get(id=object_id)
    nonhtml, tables = get_dict(request, [
        ["reports", Q(case=case)],
    ])
    if nonhtml:
        return nonhtml

    context = {}
    context.update(tables)
    context["object"] = case
    context["object_fields"] = [ {"key": f.verbose_name, "value": getattr(case, f.name)} for f in case._meta.fields ]

    return as_html(request, "child_view.html", context)