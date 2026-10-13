from typing import Any

from django.forms import ModelForm

from apps.bookings.models import Booking


class BookingAdminForm(ModelForm):

    class Meta:
        model = Booking
        fields = "__all__"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Поля нет на форме создания и в истории только для чтения.
        status_field = self.fields.get("status")
        if status_field is not None:
            # Только текущий статус и допустимые переходы из него.
            current = self.instance.status
            reachable = (
                current,
                *Booking.ALLOWED_TRANSITIONS.get(current, ()),
            )
            status_field.choices = [
                choice
                for choice in Booking.Status.choices
                if choice[0] in reachable
            ]
