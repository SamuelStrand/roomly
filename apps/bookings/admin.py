from typing import Any

from django.contrib.admin import register
from django.forms import ModelForm
from django.http import HttpRequest
from django.utils import timezone as django_timezone
from unfold.admin import ModelAdmin

from apps.bookings.forms import BookingAdminForm
from apps.bookings.models import Booking


@register(Booking)
class BookingAdmin(ModelAdmin):

    REQUEST_FIELDS = ("user", "space", "purpose", "start_time", "end_time")
    DETAIL_FIELDS = ("space", "purpose", "start_time", "end_time")
    MODERATION_FIELDS = (
        "status",
        "rejection_reason",
        "reviewed_by",
        "reviewed_at",
    )
    REVIEWED_STATUSES = (Booking.Status.APPROVED, Booking.Status.REJECTED)

    form = BookingAdminForm
    list_display = (
        "id",
        "space",
        "user",
        "start_time",
        "end_time",
        "status",
        "reviewed_by",
    )
    list_filter = ("status", "space")
    search_fields = ("purpose", "user__email", "user__full_name", "space__name")
    date_hierarchy = "start_time"
    autocomplete_fields = ("user", "space")
    list_select_related = ("user", "space", "reviewed_by")
    readonly_fields = ("reviewed_by", "reviewed_at", "created_at", "updated_at")
    actions = None

    def get_object(
        self,
        request: HttpRequest,
        object_id: str,
        from_field: str | None = None,
    ) -> Booking | None:
        booking = super().get_object(request, object_id, from_field)
        if booking is not None:
            booking.saved_status = booking.status
        return booking

    def get_fieldsets(
        self,
        request: HttpRequest,
        obj: Booking | None = None,
    ) -> list[tuple[str | None, dict[str, Any]]]:
        fieldsets: list[tuple[str | None, dict[str, Any]]] = [
            ("Request", {"fields": self.REQUEST_FIELDS}),
        ]
        if obj is not None:
            fieldsets += [
                ("Moderation", {"fields": self.MODERATION_FIELDS}),
                ("Timestamps", {"fields": ("created_at", "updated_at")}),
            ]
        return fieldsets

    def get_readonly_fields(
        self,
        request: HttpRequest,
        obj: Booking | None = None,
    ) -> tuple[str, ...]:
        readonly = tuple(self.readonly_fields)
        if obj is None:
            return readonly

        readonly += ("user",)
        status = getattr(obj, "saved_status", obj.status)
        if status != Booking.Status.PENDING:
            readonly += self.DETAIL_FIELDS + ("rejection_reason",)
        if status not in Booking.ALLOWED_TRANSITIONS:
            readonly += ("status",)
        return readonly

    def save_model(
        self,
        request: HttpRequest,
        obj: Booking,
        form: ModelForm,
        change: bool,
    ) -> None:
        if "status" in form.changed_data and obj.status in self.REVIEWED_STATUSES:
            obj.reviewed_by = request.user
            obj.reviewed_at = django_timezone.now()
        super().save_model(request, obj, form, change)

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: Booking | None = None,
    ) -> bool:
        return False
