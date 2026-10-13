from __future__ import annotations

from django.conf import settings
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

from apps.abstracts.models import AbstractBaseModel


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
