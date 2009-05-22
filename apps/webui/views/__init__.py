from reusable_table.table import register

from apps.sms.models.base import Case, ReportMalnutrition, Provider, Facility, Zone, MessageLog

register("case", Case, [
    ["District", "provider__clinic__zone__name", "{{ object.provider.clinic.zone.name }}"],
    ["GMC", "provider__clinic__name", "{{ object.provider.clinic.name }}"],
    ["Child#", "ref_id", "{{ object.ref_id }}"],
    ["Age (months)", "dob", "{{ object.months }}"],
    ["Gender", "gender", "{{ object.gender }}"],
    ["Contact", "contact", "{{ object.contact }}"],
    ["Date registered", "created_at", '{{ object.created_at|date:"d M Y" }}'],
    ["Current Nutritional Status", "", "{{ object.reportmalnutrition_set.latest.get_status_display }}"],
    ["Last Date of Child Visit", "", '{{ object.reportmalnutrition_set.latest.entered_at|date:"d M Y" }}']
    ])
        
register("reports", ReportMalnutrition, [
    ["District", "case__provider__clinic__zone__name", "{{ object.case.provider.clinic.zone.name }}"],
    ["GMC", "case__provider__clinic__name", "{{ object.case.provider.clinic.name }}"],
    ["Reporter", "case__provider__mobile", "{{ object.case.provider }}"],
    ["Child#", "case__ref_id", "{{ object.case.ref_id }}"],
    ["Height", "height", "{{ object.height }}"],
    ["Weight", "weight", "{{ object.weight }}"],
    ["MUAC", "muac", "{{ object.muac }}"],
    ["Oedema", "", ""],
    ["Diarrhea", "", ""], 
    ["Recieved", "entered_at", '{{ object.entered_at|date:"d M Y" }}'],
    ["Status", "status", "{{ object.get_status_display }}"]
    ])
    
register("providers", Provider, [
    ["Id", "", "#{{ object.id }}"],
    ["District", "clinic__zone__name", "{{ object.clinic.zone.name }}"],
    ["GMC", "clinic__name", "{{ object.clinic.name }}"],
    ["First name", "user__first_name", "{{ object.user.first_name }}"],
    ["Last name", "user__last_name", "{{ object.user.last_name }}"],
    ["Mobile", "mobile", "{{ object.mobile }}"],
    ["Quantity", "", "{{ object.quantity }}"],
    ])

register("facilities", Facility, [
    ["Id", "", "#{{ object.codename }}"],
    ["Name", "name", "{{ object.name }}"],
    ["District", "", "{{ object.zone.name }}"],
    ["Longitude", "long", "{{ object.longitude }}"],
    ["Latitude", "lat", "{{ object.latitude }}"]
])

register("zones", Zone, [
    ["Name", "name", "{{ object.name }}"],
    ["Parent", "", "{{ object.head.name }}"],
    ["Longitude", "long", "{{ object.longitude }}"],
    ["Latitude", "lat", "{{ object.latitude }}"]
])

register("message", MessageLog, [
        ["About", "mobile", "{{ object.mobile }}"],
        ["Message", "text", "{{ object.text }}"],
        ["Sent by", "sent_by", "{{ object.sent_by }}"],        
        ["Created", "created_at", '{{ object.created_at|date:"d/m/Y" }}'],
        ["Handled", "handled", "{{ object.get_handled_display }}"]
        ])