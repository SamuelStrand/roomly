from __future__ import annotations

from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db import transaction
from django.db.models import (
    PROTECT,
    SET_NULL,
    CharField,
    CheckConstraint,
    DateTimeField,
    F,
    ForeignKey,
    Index,
    Q,
    TextChoices,
    TextField,
)
from django.utils import timezone as django_timezone

from apps.abstracts.models import AbstractBaseModel
from apps.schedules.models import BlockedPeriod, OpeningHours
from apps.spaces.models import Space


class Booking(AbstractBaseModel):

    PURPOSE_MAX_LENGTH = 255
    STATUS_MAX_LENGTH = 20

    class Status(TextChoices):

        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"


    ACTIVE_STATUSES = (Status.PENDING, Status.APPROVED)

    ALLOWED_TRANSITIONS = {
        Status.PENDING: (Status.APPROVED, Status.REJECTED, Status.CANCELLED),
        Status.APPROVED: (Status.CANCELLED, Status.COMPLETED),
    }

    user = ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Applicant",
        on_delete=PROTECT,
        related_name="bookings",
    )
    space = ForeignKey(
        "spaces.Space",
        verbose_name="Room",
        on_delete=PROTECT,
        related_name="bookings",
    )
    purpose = CharField(
        verbose_name="Purpose",
        max_length=PURPOSE_MAX_LENGTH,
    )
    start_time = DateTimeField(
        verbose_name="Start time",
    )
    end_time = DateTimeField(
        verbose_name="End time",
    )
    status = CharField(
        verbose_name="Status",
        max_length=STATUS_MAX_LENGTH,
        choices=Status.choices,
        default=Status.PENDING,
    )
    rejection_reason = TextField(
        verbose_name="Rejection reason",
        blank=True,
    )
    reviewed_by = ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Reviewed by",
        on_delete=SET_NULL,
        related_name="reviewed_bookings",
        null=True,
        blank=True,
    )
    reviewed_at = DateTimeField(
        verbose_name="Reviewed at",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        ordering = ("-start_time",)
        constraints = [
            CheckConstraint(
                condition=Q(start_time__lt=F("end_time")),
                name="booking_start_before_end",
                violation_error_message="End time must be after start time.",
            ),
        ]
        indexes = [
            Index(
                fields=["space", "status", "start_time"],
                name="booking_space_status_start_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"Booking #{self.pk} ({self.get_status_display()})"

    def clean(self) -> None:
        super().clean()
        errors: dict[str, list[ValidationError]] = {}

        def fail(message: str, code: str, field: str = NON_FIELD_ERRORS) -> None:
            errors.setdefault(field, []).append(
                ValidationError(message, code=code),
            )

        now = django_timezone.now()
        saved = None
        if not self._state.adding:
            rows = type(self).objects.filter(pk=self.pk)
            if transaction.get_connection().in_atomic_block:
                rows = rows.select_for_update()
            saved = rows.first()
        is_new = saved is None

        if self.purpose and not self.purpose.strip():
            fail("Purpose is required.", "purpose_required")

        has_interval = self.start_time is not None and self.end_time is not None
        if has_interval and self.start_time >= self.end_time:
            fail("End time must be after start time.", "time_order", "end_time")
            has_interval = False

        if is_new:
            if self.status != self.Status.PENDING:
                fail("A new booking must start as pending.", "new_not_pending")
        else:
            if self.user_id != saved.user_id:
                fail("The applicant cannot be changed.", "applicant_changed")

            details_changed = (
                self.space_id,
                self.purpose,
                self.start_time,
                self.end_time,
            ) != (
                saved.space_id,
                saved.purpose,
                saved.start_time,
                saved.end_time,
            )
            if details_changed and saved.status != self.Status.PENDING:
                fail(
                    "Room, purpose and time can only be changed while the "
                    "booking is pending.",
                    "details_locked",
                )

            if self.status != saved.status:
                allowed = self.ALLOWED_TRANSITIONS.get(saved.status, ())
                if self.status not in allowed:
                    fail(
                        f"A {saved.get_status_display().lower()} booking "
                        f"cannot become "
                        f"{self.get_status_display().lower()}.",
                        "forbidden_transition",
                    )
                elif (
                    self.status == self.Status.COMPLETED
                    and saved.end_time > now
                ):
                    fail(
                        "A booking can be completed only after it has ended.",
                        "not_ended",
                    )

        if (
            self.status == self.Status.REJECTED
            and not (self.rejection_reason or "").strip()
        ):
            fail(
                "A rejection reason is required to reject a booking.",
                "rejection_reason_required",
            )

        rescheduled = not is_new and (self.start_time, self.end_time) != (
            saved.start_time,
            saved.end_time,
        )
        approving = (
            not is_new
            and self.status == self.Status.APPROVED
            and saved.status != self.Status.APPROVED
        )
        if (
            (is_new or rescheduled or approving)
            and self.start_time is not None
            and self.start_time <= now
        ):
            fail("Start time must be in the future.", "start_in_past")

        if (is_new or approving) and self.user_id and not self.user.is_active:
            fail("The applicant's account is not active.", "inactive_user")

        room_changed = not is_new and self.space_id != saved.space_id
        if (
            (is_new or room_changed or approving)
            and self.space_id
            and not self.space.is_active
        ):
            fail("The room is not active.", "inactive_space")

        if self.status in self.ACTIVE_STATUSES and has_interval and self.space_id:
            if transaction.get_connection().in_atomic_block:
                Space.objects.select_for_update().filter(
                    pk=self.space_id,
                ).first()

            overlaps = (
                type(self)
                .objects.filter(
                    space_id=self.space_id,
                    status__in=self.ACTIVE_STATUSES,
                    deleted_at__isnull=True,
                    start_time__lt=self.end_time,
                    end_time__gt=self.start_time,
                )
                .exclude(pk=self.pk)
            )
            if overlaps.exists():
                fail(
                    "The room already has a pending or approved booking "
                    "in this interval.",
                    "overlap",
                )

            local_start = django_timezone.localtime(self.start_time)
            local_end = django_timezone.localtime(self.end_time)
            if local_start.date() != local_end.date():
                fail(
                    "A booking must start and end on the same day.",
                    "multi_day",
                )
            elif not OpeningHours.objects.filter(
                space_id=self.space_id,
                weekday=local_start.weekday(),
                opens_at__lte=local_start.time(),
                closes_at__gte=local_end.time(),
            ).exists():
                fail(
                    "The room is closed during this interval.",
                    "closed_hours",
                )

            if BlockedPeriod.objects.filter(
                space_id=self.space_id,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
            ).exists():
                fail("The room is blocked during this interval.", "blocked")

        if errors:
            raise ValidationError(errors)
