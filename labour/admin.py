from django.contrib import admin
from .models import LabourEntry

@admin.register(LabourEntry)
class LabourEntryAdmin(admin.ModelAdmin):
    list_display = ['pargi_name', 'labour_name', 'date', 'day', 'in_time', 'out_time', 
                    'quantity', 'rupees_per_head', 'total_amount', 'owner_name']
    list_filter = ['date', 'pargi_name', 'owner_name', 'land_crop_name']
    search_fields = ['pargi_name', 'labour_name', 'owner_name', 'land_crop_name', 'user__username']
    readonly_fields = ['total_amount', 'day']
    
    fieldsets = (
        ('Date & Time', {
            'fields': ('date', 'day', 'in_time', 'out_time')
        }),
        ('Labour Details', {
            'fields': ('pargi_name', 'labour_name', 'quantity', 'rupees_per_head', 'total_amount')
        }),
        ('Location Details', {
            'fields': ('land_crop_name', 'owner_name')
        }),
        ('Additional Info', {
            'fields': ('notes', 'user')
        }),
    )