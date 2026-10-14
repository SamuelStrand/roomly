from typing import Any

from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpRequest
from unfold.admin import ModelAdmin

from apps.notifications.models import Notification


Fieldsets = tuple[tuple[str, dict[str, Any]], ...]


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    """Notification model admin configuration class."""

    list_display = (
        "id",
        "recipient_email",
        "booking",
        "short_message",
        "is_read",
        "created_at",
    )
    list_display_links = ("id",)
    list_filter = ("is_read", "recipient")
    search_fields = ("message", "recipient__email")
    autocomplete_fields = ("recipient", "booking")
    list_select_related = ("recipient", "booking")
    ordering = ("-created_at",)
    list_per_page = 50
    list_filter_sheet = True
    readonly_fields = (
        "created_at",
        "updated_at",
        "deleted_at",
    )
    actions = ("mark_as_read",)

    fieldsets: Fieldsets = (
        (
            "Notification",
            {
                "classes": ("tab",),
                "fields": (
                    "recipient",
                    "booking",
                    "message",
                ),
            },
        ),

        (
            "Read status",
            {
               "classes": ("tab",),
                "fields": (
                    "is_read",
                ), 
            },
        ),
        
        (
            "Dates",
            {
                "classes": ("tab",),
                "fields": (
                    "created_at",
                    "updated_at",
                    "deleted_at",
                ),
            },
        ),
    )

    add_fieldsets: Fieldsets = (
        (
            "Notification",
            {
                "classes": ("tab",),
                "fields": (
                    "recipient",
                    "booking",
                    "message",
                ),
            },
        ),
    )


    def get_fieldsets(
        self,
        request: HttpRequest,
        obj: Notification | None = None,
    ) -> Fieldsets:
        """Select fieldset for managing notifications."""
        if obj is None:
            return self.add_fieldsets
        return self.fieldsets

    def get_readonly_fields(
            self,
            request: HttpRequest,
            obj: Notification | None = None,
    ) -> tuple[str, ...]:
        """Readonly."""

        fields = tuple(super().get_readonly_fields(request, obj))

        if obj is not None:
            return fields + (
                "recipient",
                "booking",
                "message",
            )
        return fields
    
    @admin.display(
        description="Recipient email", 
        ordering="recipient__email"
    )
    def recipient_email(self, obj: Notification) -> str:
        "Show the notification recipirnt email. "
        return obj.recipient.email
    
    @admin.display(description="Message")
    def short_message(self, obj: Notification) -> str:
        """Show shortened notification message."""

        message = obj.message.strip()

        if len(message) > 80:
            return f"{message[:77]}..."

        return message
    

    @admin.action(
        description="Mark selected unread notification as read.", 
        permissions=["change"]
    )
    def mark_as_read(
        self, 
        request: HttpRequest,
        queryset: QuerySet[Notification], 
    ) -> None:  
        """Mark selected unread notification as read."""

        if not self.has_change_permission(request):
            raise PermissionDenied
        
        count = queryset.filter(is_read=False).update(is_read=True)

        self.message_user(
            request,
            f"Marked {count} notification(s) as read.",
            level=messages.SUCCESS,
        )
    
    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: Notification | None = None,
    ) -> bool:
        """Disable deletion through admin."""

        return False