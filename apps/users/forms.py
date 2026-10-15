from typing import Any

from django.contrib.auth.forms import BaseUserCreationForm, UserChangeForm
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.forms import UnfoldReadOnlyPasswordHashWidget
from unfold.widgets import UnfoldAdminPasswordWidget

from apps.users.models import CustomUser


class CustomUserCreationForm(BaseUserCreationForm):
    """Validate matching passwords and hash them when creating an account."""

    class Meta:
        """Replace Django's username model and fields with Roomly's user."""

        model = CustomUser
        fields = (
            "email",
            "full_name",
            "phone",
            "identity_number",
            "role",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )
        field_classes = {}

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Style required password inputs without changing validation."""
        super().__init__(*args, **kwargs)
        for name in ("password1", "password2"):
            self.fields[name].widget = UnfoldAdminPasswordWidget(
                attrs={"autocomplete": "new-password"},
            )

    def clean_email(self) -> str:
        """Normalize the domain before checking the unique email address."""
        return CustomUser.objects.normalize_email(self.cleaned_data["email"])


class CustomUserChangeForm(UserChangeForm):
    """Edit account details while retaining the disabled password hash."""

    class Meta:
        """Expose account fields and Django's read-only password widget."""

        model = CustomUser
        fields = (
            "email",
            "full_name",
            "password",
            "phone",
            "identity_number",
            "role",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )
        field_classes = {}

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Style the password hash when the Admin exposes that field."""
        super().__init__(*args, **kwargs)
        password = self.fields.get("password")
        if password is not None:
            password.widget = UnfoldReadOnlyPasswordHashWidget()
            password.help_text = format_html(
                "{} {}",
                _("Passwords cannot be viewed."),
                format_html(
                    '<a href="{}" class="text-primary-600 '
                    'dark:text-primary-500">{}</a>',
                    "../password/",
                    _("Change password"),
                ),
            )

    def clean_email(self) -> str:
        """Apply the manager's email convention to profile edits too."""
        return CustomUser.objects.normalize_email(self.cleaned_data["email"])
