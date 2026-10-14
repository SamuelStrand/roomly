from django.conf import settings

from django.db.models import BooleanField, ForeignKey, TextField, PROTECT
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from apps.abstracts.models import AbstractBaseModel

class Notification(AbstractBaseModel):
    """Manually created notifications for bookings."""
    recipient = ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=PROTECT,
        related_name="notifications",
        verbose_name="Recipient"
    )

    booking = ForeignKey(
        to="bookings.Booking",
        on_delete=PROTECT,
        related_name="notifications",
        verbose_name="Booking"
    )

    message = TextField(
        verbose_name="Message"
    )

    is_read = BooleanField(
        verbose_name="Is read",
        default=False,
    )


    class Meta:
        """Admin visible name and oredering."""
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]

    def clean(self) -> None:
        """Require nonblank text and recipient related to booking."""
        
        super().clean()
        errors: dict[str, str] = {}

        if not (self.message or "").strip():
            errors["message"] = "Message need to be filled."

        if (self.recipient_id is not None and self.booking_id is not None):
            try:
                booking_user_id = self.booking.user_id
            except ObjectDoesNotExist:
                booking_user_id = None

            if (
                booking_user_id is not None
                and self.recipient_id != booking_user_id
            ):
                errors["recipient"] = (
                    "Recipirnt should match booking creator"
            )
        
        if errors:
            raise ValidationError(errors)



    def __str__(self) -> str:
        """Readable value."""
        return f"Notification #{self.pk}"