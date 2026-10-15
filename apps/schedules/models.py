from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from apps.abstracts.models import AbstractBaseModel


class OpeningHours(AbstractBaseModel):
    """Opening hours for a room."""

    space = models.ForeignKey(
        to="spaces.Space",
        on_delete=models.PROTECT,
        related_name="opening_hours",
    )

    class Weekday(models.IntegerChoices):
        """Days of the week, following Python's weekday numbering."""

        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    weekday = models.IntegerField(choices=Weekday.choices)
    opens_at = models.TimeField()
    closes_at = models.TimeField()

    class Meta:
        """Database configuration for opening hours."""

        verbose_name = "Opening hours"
        verbose_name_plural = "Opening hours"

        constraints = (
            models.UniqueConstraint(
                fields=("space", "weekday"),
                name="unique_space_weekday",
            ),
            models.CheckConstraint(
                condition=Q(weekday__gte=0, weekday__lte=6),
                name="weekday_range_0_6",
            ),
            models.CheckConstraint(
                condition=Q(opens_at__lt=F("closes_at")),
                name="opening_before_closing",
            ),
        )

    def clean(self) -> None:
        """Validate hours, protect the schedule key, and preserve bookings."""
        super().clean()
        errors: dict[str, str] = {}

        if (
            self.opens_at is not None
            and self.closes_at is not None
            and self.opens_at >= self.closes_at
        ):
            errors["closes_at"] = "Closing time must be later than opening time."

        original = None
        if self.pk:
            original = type(self).objects.filter(pk=self.pk).first()

        if original is not None:
            if original.space_id != self.space_id:
                errors["space"] = (
                    "The room cannot be changed for an existing opening-hours record."
                )

            if original.weekday != self.weekday:
                errors["weekday"] = (
                    "The weekday cannot be changed for an existing "
                    "opening-hours record."
                )

        valid_hours = (
            self.space_id is not None
            and self.opens_at is not None
            and self.closes_at is not None
            and self.opens_at < self.closes_at
            and 0 <= self.weekday <= 6
        )

        if valid_hours:
            from apps.bookings.models import Booking

            now = timezone.now()
            bookings = Booking.objects.filter(
                space_id=self.space_id,
                status__in=Booking.ACTIVE_STATUSES,
                end_time__gt=now,
            )

            for booking in bookings:
                local_start = timezone.localtime(booking.start_time)
                local_end = timezone.localtime(booking.end_time)

                if local_start.weekday() != self.weekday:
                    continue

                if (
                    local_start.time() < self.opens_at
                    or local_end.time() > self.closes_at
                ):
                    errors["opens_at"] = (
                        "The proposed opening hours conflict with an active booking."
                    )
                    break

        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.space} - {self.get_weekday_display()}"


class BlockedPeriod(AbstractBaseModel):
    """A period when a room is unavailable."""

    REASON_MAX_LEN = 255

    space = models.ForeignKey(
        to="spaces.Space",
        on_delete=models.PROTECT,
        related_name="blocked_periods",
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    reason = models.CharField(max_length=REASON_MAX_LEN)

    class Meta:
        """Database configuration for blocked periods."""

        verbose_name = "Blocked period"
        verbose_name_plural = "Blocked periods"

        constraints = (
            models.CheckConstraint(
                condition=Q(start_time__lt=F("end_time")),
                name="blocked_period_start_before_end",
            ),
        )

        indexes = (
            models.Index(
                fields=("space", "start_time"),
                name="blocked_space_start_idx",
            ),
        )

    def clean(self) -> None:
        """Validate the period and prevent conflicts with active bookings."""
        super().clean()
        errors: dict[str, str] = {}

        if (
            self.start_time is not None
            and self.end_time is not None
            and self.start_time >= self.end_time
        ):
            errors["end_time"] = "End time must be later than start time."

        if not self.reason or not self.reason.strip():
            errors["reason"] = "Reason cannot be blank."

        valid_interval = (
            self.space_id is not None
            and self.start_time is not None
            and self.end_time is not None
            and self.start_time < self.end_time
        )

        if valid_interval:
            from apps.bookings.models import Booking

            now = timezone.now()
            overlapping_bookings = Booking.objects.filter(
                space_id=self.space_id,
                status__in=Booking.ACTIVE_STATUSES,
                start_time__lt=self.end_time,
                end_time__gt=max(now, self.start_time),
            )

            if overlapping_bookings.exists():
                errors["start_time"] = "This blocked period overlaps an active booking."

        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.space} - {self.start_time}"
