from django.contrib.auth.forms import BaseUserCreationForm, UserChangeForm

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

    def clean_email(self) -> str:
        """Apply the manager's email convention to profile edits too."""
        return CustomUser.objects.normalize_email(self.cleaned_data["email"])
