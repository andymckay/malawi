from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from models.base import Zone, Facility, Case, Provider, MessageLog, ReportMalnutrition
from models.profile import Profile

class CaseAdmin(admin.ModelAdmin):
    list_display = ("ref_id", "first_name", "last_name", "gender", "dob", "zone")
    
admin.site.register(Case, CaseAdmin)
admin.site.register(Provider)

admin.site.register(Facility)

class MessageLogAdmin(admin.ModelAdmin):
    list_display = ("mobile", "sent_by", "text", "created_at", "was_handled")
    list_filter = ("was_handled",)
    
admin.site.register(MessageLog, MessageLogAdmin)

class ZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "head", "get_category_display")

admin.site.register(Zone, ZoneAdmin)
admin.site.register(Profile)
admin.site.register(ReportMalnutrition)