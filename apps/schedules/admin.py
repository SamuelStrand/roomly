from typing import Any

from django import forms
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpRequest
from unfold.admin import ModelAdmin, TabularInline

from apps.schedules.models import BlockedPeriod, OpeningHours


class OpeningHoursInlineForm(forms.ModelForm):
    """Form for opening hours displayed inside a room."""

    class Meta:
        model = OpeningHours
        fields = ("weekday", "opens_at", "closes_at")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields["weekday"].disabled = True


class OpeningHoursInline(TabularInline):
    """Display opening hours inline on the room admin page."""

    model = OpeningHours
    form = OpeningHoursInlineForm
    extra = 0
    can_delete = False
    ordering = ("weekday",)
    fields = ("weekday", "opens_at", "closes_at")

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: Any = None,
    ) -> bool:
        """Prevent deleting opening hours through the inline."""
        return False


@admin.register(OpeningHours)
class OpeningHoursAdmin(ModelAdmin):
    """Configure the admin interface for opening hours."""

    list_display = ("space", "weekday", "opens_at", "closes_at")
    list_filter = ("space", "weekday")
    search_fields = ("space__name",)
    autocomplete_fields = ("space",)
    ordering = ("space", "weekday")

    fieldsets = (
        (
            "Room and day",
            {"fields": ("space", "weekday")},
        ),
        (
            "Opening hours",
            {"fields": ("opens_at", "closes_at")},
        ),
        (
            "Record information",
            {"fields": ("created_at", "updated_at")},
        ),
    )

    readonly_fields = ("created_at", "updated_at")

    def get_readonly_fields(
        self,
        request: HttpRequest,
        obj: OpeningHours | None = None,
    ) -> tuple[str, ...]:
        """Prevent changing room and weekday after creation."""
        fields = list(super().get_readonly_fields(request, obj))

        if obj is not None:
            fields.extend(("space", "weekday"))

        return tuple(fields)

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: OpeningHours | None = None,
    ) -> bool:
        """Disable deleting opening hours in the admin."""
        return False

    def get_actions(self, request: HttpRequest) -> dict[str, Any]:
        """Remove the bulk-delete action from the admin list."""
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions

    def delete_model(
        self,
        request: HttpRequest,
        obj: OpeningHours,
    ) -> None:
        """Reject direct admin deletion of an opening-hours record."""
        raise PermissionDenied("Opening hours cannot be deleted.")

    def delete_queryset(
        self,
        request: HttpRequest,
        queryset: QuerySet[OpeningHours],
    ) -> None:
        """Reject bulk deletion of opening-hours records."""
        raise PermissionDenied("Opening hours cannot be deleted.")

    def get_queryset(
        self,
        request: HttpRequest,
    ) -> QuerySet[OpeningHours]:
        """Load related rooms efficiently when listing opening hours."""
        return super().get_queryset(request).select_related("space")


@admin.register(BlockedPeriod)
class BlockedPeriodAdmin(ModelAdmin):
    """Configure the admin interface for blocked periods."""

    list_display = ("space", "start_time", "end_time", "reason")
    list_filter = ("space",)
    search_fields = ("space__name", "reason")
    autocomplete_fields = ("space",)
    ordering = ("space", "start_time")

    fieldsets = (
        (
            "Room",
            {"fields": ("space",)},
        ),
        (
            "Unavailable interval",
            {"fields": ("start_time", "end_time", "reason")},
        ),
        (
            "Record information",
            {"fields": ("created_at", "updated_at")},
        ),
    )

    readonly_fields = ("created_at", "updated_at")

    def delete_model(
        self,
        request: HttpRequest,
        obj: BlockedPeriod,
    ) -> None:
        """Use physical deletion for single and bulk block removal."""
        self.delete_queryset(
            request,
            self.get_queryset(request).filter(pk=obj.pk),
        )

    def get_queryset(
        self,
        request: HttpRequest,
    ) -> QuerySet[BlockedPeriod]:
        """Load related rooms efficiently when listing blocked periods."""
        return super().get_queryset(request).select_related("space")
