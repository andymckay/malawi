from reusable_table.table import register

from apps.sms.models.base import Case, ReportMalnutrition, Provider, Facility, Zone, MessageLog

register("case", Case, [
    ["Child#", "ref_id", "{{ object.ref_id }}"],
    ["District", "provider__clinic__zone__name", "{{ object.provider.clinic.zone.name }}"],
    ["GMC", "provider__clinic__name", "{{ object.provider.clinic.name }}"],
    ["Months", "dob", "{{ object.months }}"],
    ["Gender", "gender", "{{ object.gender }}"],
    ["Contact", "contact", "{{ object.contact }}"],
    ["Registered", "created_at", '{{ object.created_at|date:"d M y H:i" }}'],
    ["Nutritional Status", "", "{{ object.reportmalnutrition_set.latest.get_status_display }}"],
    ["Last Visit", "", '{{ object.reportmalnutrition_set.latest.entered_at|date:"d M y H:i" }}'],
    ["ID", "id", "{{ object.id }}"]
    ])
        
register("reports", ReportMalnutrition, [
    ["District", "case__provider__clinic__zone__name", "{{ object.case.provider.clinic.zone.name }}"],
    ["GMC", "case__provider__clinic__name", "{{ object.case.provider.clinic.name }}"],
    ["HSA", "case__provider__mobile", "{{ object.case.provider }}"],
    ["Child#", "case__ref_id", "{{ object.case.ref_id }}"],
    ["Gender", "case__gender", "{{ object.case.gender }}"],
    ["Age (months)", "case__dob", "{{ object.case.get_dictionary.raw_months }}"],
    ["Height", "height", "{{ object.height }}"],
    ["Weight", "weight", "{{ object.weight }}"],
    ["MUAC", "muac", "{{ object.muac }}"],
    ["Oedema", "", "{{ object.get_dictionary.oedema }}"],
    ["Diarrhea", "", "{{ object.get_dictionary.diarrhea }}"], 
    ["Recieved", "entered_at", '{{ object.entered_at|date:"d M y H:i" }}'],
    ["Status", "status", "{{ object.get_status }}"]
    ])
    
register("providers", Provider, [
    ["Id", "", "#{{ object.id }}"],
    ["District", "clinic__zone__name", "{{ object.clinic.zone.name }}"],
    ["GMC", "clinic__name", "{{ object.clinic.name }}"],
    ["First name", "user__first_name", "{{ object.user.first_name }}"],
    ["Last name", "user__last_name", "{{ object.user.last_name }}"],
    ["Mobile", "mobile", "{{ object.mobile }}"],
    ["Quantity Pass", "", "{{ object.quantity_pass }}"],
    ["Quantity Fail", "", "{{ object.quantity_fail }}"],
    ])

register("facilities", Facility, [
    ["Id", "", "#{{ object.codename }}"],
    ["Name", "name", "{{ object.name }}"],
    ["District", "", "{{ object.zone.name }}"],
    ["Longitude", "long", "{{ object.lon }}"],
    ["Latitude", "lat", "{{ object.lat }}"]
])

register("zones", Zone, [
    ["Name", "name", "{{ object.name }}"],
    ["Parent", "", "{{ object.head.name }}"],
    ["Longitude", "long", "{{ object.lon }}"],
    ["Latitude", "lat", "{{ object.lat }}"]
])

register("message", MessageLog, [
        ["About", "mobile", "{{ object.mobile }}"],
        ["Message", "text", "{{ object.text }}"],
        ["Sent by", "sent_by", "{{ object.sent_by }}"],        
        ["Created", "created_at", '{{ object.created_at|date:"d/m/Y" }}'],
        ["Error", "form_error", "{{ object.form_error }}"]
        ])