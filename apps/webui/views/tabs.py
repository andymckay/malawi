from reusable_table.table import get_dict, get
from django.db.models import Q
from malnutrition.ui.views.shortcuts import as_html, login_required
from apps.sms.models.base import Case

@login_required
def hsa(request):
    nonhtml, tables = get_dict(request, [
        ["providers", Q()],
    ])
    if nonhtml:
        return nonhtml

    context = {}
    context.update(tables)

    return as_html(request, "hsa.html", context)

@login_required
def child_list(request):
    nonhtml, tables = get_dict(request, [
        ["case", Q()],
        ["reports", Q()]
    ])
    if nonhtml:
        return nonhtml

    context = {}
    context.update(tables)

    return as_html(request, "child_list.html", context)
    
@login_required
def setup(request):
    nonhtml, tables = get(request, [
        ["facilities", Q()],
        ["zones", Q()],
        ["message", Q(form_error=False)],
        ["message", Q(form_error=True)],
    ])
    if nonhtml:
        return nonhtml

    context = {}
    context["facilities"] = tables[0]
    context["zones"] = tables[1]
    context["message_pass"] = tables[2]
    context["message_fail"] = tables[3]

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