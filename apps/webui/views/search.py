from malnutrition.ui.views.shortcuts import as_html, login_required
from django.db.models import Q
from reusable_table.table import get

@login_required
def view(request):
    term = request.GET.get("q")
    query = Q(ref_id__icontains=term)

    nonhtml, tables = get(request, [ ["case", query], ])
    if nonhtml: 
        return nonhtml

    return as_html(request, "searchview.html", { "search": tables[0], })