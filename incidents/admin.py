from django.contrib import admin

from .models import Incident, IncidentHistory


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('incident_id', 'title', 'priority', 'status', 'assigned_engineer', 'sla_status_display', 'created_date', 'updated_at')
    list_filter = ('priority', 'status', 'created_date', 'sla_deadline')
    search_fields = ('title', 'description', 'assigned_engineer', 'incident_id')
    ordering = ('-created_date',)
    readonly_fields = ('incident_id', 'created_date', 'updated_at', 'sla_deadline', 'sla_status_display')

    fieldsets = (
        ('Basic Information', {
            'fields': ('incident_id', 'title', 'description', 'priority', 'status')
        }),
        ('Assignment', {
            'fields': ('assigned_engineer',)
        }),
        ('Resolution', {
            'fields': ('resolution_notes',)
        }),
        ('SLA Information', {
            'fields': ('sla_deadline', 'sla_status_display')
        }),
        ('Timestamps', {
            'fields': ('created_date', 'updated_at')
        }),
    )


@admin.register(IncidentHistory)
class IncidentHistoryAdmin(admin.ModelAdmin):
    list_display = ('incident', 'action', 'changed_by', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('incident__title', 'incident__incident_id', 'changed_by', 'description')
    ordering = ('-timestamp',)
    readonly_fields = ('incident', 'action', 'description', 'changed_by', 'timestamp')
