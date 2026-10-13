from django.db import models

from django.db.models import BooleanField, ForeignKey, TextField, PROTECT
from django.core.exceptions import ObjectDoesNotExist

from apps.abstracts.models import AbstractBaseModel
from django.conf import settings

class Notifications(AbstractBaseModel):
    """Manually created notifications for bookings."""
    recipient = ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=PROTECT,
        related_name="notification",
        verbose_name="Recipient"
    )

    booking = ForeignKey(
        to="bookings.Booking",
        on_delete=PROTECT,
        related_name="notification",
        verbose_name="Booking"
    )

    message = TextField(
        verbose_name="Message body"
    )

    is_read = BooleanField(
        default=False,
        verbose_name="Is read"
    )


    class Meta:
        """Admin visible name and oredering."""
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["created_at"]

    def clean(self):
        """Require nonblank text and recipient related to booking."""
        super().clean()
        errors: dict[str, str] = {}

        if not (self.message or "").strip():
            errors["messages"] = "Message need to be filled."

        if (self.recipient_id and self.booking_id):
            try:
                booking_user_id = self.booking_user_id
            except (ObjectDoesNotExist, AttributeError):
                pass

        else:
            if self.recipient_id != booking_user_id:
                errors["recipient"] = ("Recipirnt should match booking creator")


        def __str__(self) -> str:
            """Short value."""
            return f"Notification{self.pk}"