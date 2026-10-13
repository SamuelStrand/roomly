from django.contrib import admin
from django.core.exceptions import PermissionDenied
from unfold.admin import ModelAdmin, TabularInline

from apps.schedules.models import BlockedPeriod, OpeningHour


class OpeningHourInline(TabularInline):
    """Display opening hours inline on the room admin page."""
    
    model = OpeningHour
    extra = 0
    can_delete = False
    ordering = ("weekday",)
    
    fields = ("weekday", "opens_at", "closes_at")
    
    def get_readonly_fields(self, request, obj = None):
        """Make weekday read-only for existing opening-hour records."""
        
        if obj is not None:
            return("weekday",)
        return()
    
    def has_delete_permission(self, request, obj = None):
        """Prevent deleting opening through the inline."""
        return False
    
@admin.register(OpeningHour)
class OpeningHourAdmin(ModelAdmin):
    """Configure the admin interface for opening hours."""
    
    list_display = ("space", "weekday", "opens_at", "closes_at")
    list_filter = ("space", "weekday")
    search_fields = ("space__name")
    autocomplete_fields = ("space",)
    ordering = ("space", "weekday")
    
    fieldsets = (
        (
            "Room and day",
            {"fields":("space", "weekday")},
        ),
        (
            "Opening hours",
            {"fields":("opens_at", "closes_at")},
        ),
        (
            "Record information",
            {"fields":("created_at", "updated_at")},
        ),
    )
    
    readonly_fields = ("created_at", "updated_at")
    
    def get_readonly_fields(self, request, obj = None):
        """Prevent changing room and weekday after record is created"""
        
        fields = list(super().get_readonly_fields(request, obj))
        
        if obj is not None:
           fields.extend(("space", "weekday"))
           
        return tuple(fields)
    
    def has_delete_permission(self, request, obj = None):
        """Disable deletion of openning-hour records in the admin."""
        
        return False
    
    def get_actions(self, request):
        """Remove the bulk-delete action from the admin list."""
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions
    
    def delete_model(self, request, obj):
        """Reject direct admin deletion of an opening-hour record."""
        raise PermissionDenied("Opening hours canot be deleted")
    
    def get_queryset(self, request):
        """Load related rooms efficiently when listing opening hours."""
        return super().get_queryset(request).select_related("space")
    
    
@admin.register(BlockedPeriod)
class BlockedPeriodAdmin(ModelAdmin):
    """Configure the admin interface for blocked periods."""
    
    list_display = (
        "space",
        "start_time",
        "end_time",
        "reason",
    )
    list_filter = ("space")
    search_fields = ("space__name", "reason")
    autocomplete_fields = ("space")
    ordering = ("space", "start_time")
    
    fieldsets = (
        (
            "Room",
            {"fields":("space",)},
        ),
        (
            "Unavailable interval",
            {"fields":("start_time", "end_time", "reason")},
        ),
        (
            "Record information",
            {"fields":("created_at", "updated_at")},
        ),
    )
    
    readonly_fields = ("created_at", "updated_at")
    
    def get_queryset(self, request):
         """Load related rooms efficiently when listing blocked periods."""
         
         return super().get_queryset(request).select_related("space")