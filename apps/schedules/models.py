from django.core.exceptions import ValidationError
from django.db.models import (
    PROTECT,
    CharField,
    CheckConstraint,
    DateTimeField,
    F,
    ForeignKey,
    Index,
    IntegerChoices,
    IntegerField,
    Q,
    TimeField,
    UniqueConstraint,
)

from apps.abstracts.models import AbstractBaseModel


class OpeningHour(AbstractBaseModel):
    """Opening hours database table."""
    space = ForeignKey(
        to="spaces.Space",
        on_delete=PROTECT,
        related_name="opening_hours",
    )
    
    class Weekday(IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"
    
    weekday = IntegerField(
        choices=Weekday.choices,
    )
    
    opens_at = TimeField()
    
    closes_at = TimeField()
    
    class Meta:
        """Meta data for the table."""
        
        verbose_name = "Opening hour"
        verbose_name_plural = "Opening hours"
        
        constraints = [
            UniqueConstraint(
                fields=("space", "weekday"),
                name="unique_space_weekday"
            ),
            CheckConstraint(
                condition=Q(
                    weekday__gte=0,
                    weekday__lte=6
                ),
                name="weekday_range_0_6",
            ),
            CheckConstraint(
                condition=Q(opens_at__lt=F("closes_at")),
                name="opening_before_closing",
            ),
        ]
        
    def clean(self) -> None:
        """Validate opening hours."""
        super().clean()
        
        errors = {}
        
        if (
            self.opens_at is not None 
            and self.closes_at is not None 
            and self.opens_at >= self.closes_at
        ):
            errors["closes_at"] = (
                "Closing time must be later than opening time."
            )
            
        if self.pk and self.space_id is not None:
            original = type(self).objects.filter(pk=self.pk).first()
            
            if original is not None:
                if original.space_id != self.space_id:
                    errors["space"] = (
                        "The room cannot be changed gor an existing opening-hours record."
                    )
                    
                if original.weekday != self.weekday:
                    errors["weekday"] = (
                        "The weekday cannot be changed for an existing opening-hours record."
                    )
        if errors:
            raise ValidationError(errors)
            
            
    def __str__(self) -> str:
        return f"{self.space} - {self.get_weekday_display()}"


class BlockedPeriod(AbstractBaseModel):
    """Blocked period database table."""
    
    REASON_MAX_LEN = 255
    
    space = ForeignKey(
        to="spaces.Space",
        on_delete=PROTECT,
        related_name="blocked_periods",
    )
    
    start_time = DateTimeField()
    
    end_time = DateTimeField()
    
    reason = CharField(
        max_length=REASON_MAX_LEN,
    )
    
    class Meta:
        """Meta data for the table."""
        
        verbose_name = "Blocked period"
        verbose_name_plural = "Blocked periods"
        
        constraints = [
            CheckConstraint(
                condition=Q(start_time__lt=F("end_time")),
                name="blocked_period_start_before_end",
            ),
        ]
        
        indexes = [
            Index(
                fields=("space", "start_time"),
                name="blocked_space_start_idx",
            ),
        ]
        
    def clean(self) -> None:
        """Validate blocked period."""
        
        super().clean()
        
        errors = {}
        
        if (
            self.start_time is not None
            and self.end_time is not None
            and self.start_time >= self.end_time
        ):
            errors["end_time"] = (
                "End time must be later than start time."
            )
            
        if not self.reason or not self.reason.strip():
            errors["reason"] = "Reason cannot be blank."
            
        if errors:
            raise ValidationError(errors)
        
    def __str__(self) -> str:
        return f"{self.space} - {self.start_time}"