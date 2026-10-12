
from typing import Any

from django.contrib import admin, messages
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import ngettext

from apps.users.forms import CustomUserChangeForm, CustomUserCreationForm
from apps.users.models import CustomUser

Fieldsets = tuple[tuple[str, dict[str, Any]], ...]


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Let superusers manage accounts and authorized staff view profiles."""

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = (
        "id",
        "email",
        "full_name",
        "role",
        "is_active",
        "is_deleted",
    )
    list_display_links = ("id", "email")
    list_filter = (
        "role",
        "is_active",
        "is_staff",
        ("deleted_at", admin.EmptyFieldListFilter),
    )
    search_fields = ("email", "full_name", "phone", "identity_number")
    ordering = ("email",)
    list_per_page = 50
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "deleted_at",
        "last_login",
    )
    filter_horizontal = ("groups", "user_permissions")
    actions = ("mark_as_deleted",)

    fieldsets: Fieldsets = (
        (
            "Profile",
            {
                "fields": (
                    "id",
                    "email",
                    "full_name",
                    "phone",
                    "identity_number",
                    "role",
                ),
            },
        ),
        ("Password", {"fields": ("password",)}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "Dates",
            {
                "fields": (
                    "last_login",
                    "created_at",
                    "updated_at",
                    "deleted_at",
                ),
            },
        ),
    )
    add_fieldsets: Fieldsets = (
        (
            "Profile",
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "full_name",
                    "phone",
                    "identity_number",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )
    view_fieldsets: Fieldsets = (
        (
            "Profile",
            {
                "fields": (
                    "id",
                    "email",
                    "full_name",
                    "phone",
                    "identity_number",
                    "role",
                    "is_active",
                ),
            },
        ),
        (
            "Dates",
            {
                "fields": (
                    "last_login",
                    "created_at",
                    "updated_at",
                    "deleted_at",
                ),
            },
        ),
    )

    def get_fieldsets(
        self,
        request: HttpRequest,
        obj: CustomUser | None = None,
    ) -> Fieldsets:
        """Hide password and authorization fields from view-only staff."""
        if not request.user.is_superuser:
            return self.view_fieldsets
        if obj is None:
            return self.add_fieldsets
        return self.fieldsets

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Require a superuser even if add permission was granted directly."""
        return request.user.is_superuser and super().has_add_permission(
            request,
        )

    def has_change_permission(
        self,
        request: HttpRequest,
        obj: CustomUser | None = None,
    ) -> bool:
        """Restrict profile, permission and password changes to superusers."""
        return request.user.is_superuser and super().has_change_permission(
            request,
            obj,
        )

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: CustomUser | None = None,
    ) -> bool:
        """Disable standard single and bulk user deletion in this Admin."""
        return False

    @admin.display(boolean=True, description="Deleted")
    def is_deleted(self, obj: CustomUser) -> bool:
        """Show the marker using Django's standard boolean icon."""
        return obj.deleted_at is not None

    @admin.action(
        description="Mark selected users as deleted",
        permissions=["change"],
    )
    def mark_as_deleted(
        self,
        request: HttpRequest,
        queryset: QuerySet[CustomUser],
    ) -> None:
        """Mark users atomically without changing their other fields."""
        if not self.has_change_permission(request):
            raise PermissionDenied

        marked_count = 0
        with transaction.atomic(using=queryset.db):
            for user in queryset.filter(deleted_at__isnull=True):
                user.delete(using=queryset.db)
                self.log_change(request, user, "Marked as deleted.")
                marked_count += 1

        message = ngettext(
            "%(count)d user was marked as deleted. Activity is unchanged.",
            "%(count)d users were marked as deleted. Activity is unchanged.",
            marked_count,
        ) % {"count": marked_count}
        self.message_user(request, message, level=messages.SUCCESS)


admin.site.unregister(Group)


@admin.register(Group)
class RestrictedGroupAdmin(GroupAdmin):
    """Keep Django's Groups UI with authorization limited to superusers."""

    def has_module_permission(self, request: HttpRequest) -> bool:
        """Show authorization administration only to superusers."""
        return request.user.is_superuser and super().has_module_permission(
            request,
        )

    def has_view_permission(
        self,
        request: HttpRequest,
        obj: Group | None = None,
    ) -> bool:
        """Protect group details even when a view permission was granted."""
        return request.user.is_superuser and super().has_view_permission(
            request,
            obj,
        )

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Allow only superusers to create groups."""
        return request.user.is_superuser and super().has_add_permission(
            request,
        )

    def has_change_permission(
        self,
        request: HttpRequest,
        obj: Group | None = None,
    ) -> bool:
        """Prevent non-superusers from changing group membership rights."""
        return request.user.is_superuser and super().has_change_permission(
            request,
            obj,
        )

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: Group | None = None,
    ) -> bool:
        """Allow only superusers to remove permission groups."""
        return request.user.is_superuser and super().has_delete_permission(
            request,
            obj,
        )
