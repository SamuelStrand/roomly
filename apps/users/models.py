from __future__ import annotations

from typing import Any

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db.models import (
    BooleanField,
    CharField,
    EmailField,
    TextChoices,
)

from apps.abstracts.models import AbstractBaseModel


class CustomUserManager(BaseUserManager):
    """Create accounts using Django's email and password conventions."""

    def __obtain_user_instance(
        self,
        email: str,
        full_name: str,
        **kwargs: Any,
    ) -> CustomUser:
        """Validate required values and build an unsaved user."""
        if not email or not email.strip():
            raise ValidationError(
                "The email must not be empty.",
                code="email_empty",
            )

        if not full_name or not full_name.strip():
            raise ValidationError(
                "The full name must not be empty.",
                code="full_name_empty",
            )

        return self.model(
            email=self.normalize_email(email.strip()),
            full_name=full_name.strip(),
            **kwargs,
        )

    def create_user(
        self,
        email: str,
        full_name: str,
        password: str | None = None,
        **kwargs: Any,
    ) -> CustomUser:
        """Hash a password and save an account to this manager's database."""
        kwargs.setdefault("is_active", True)
        kwargs.setdefault("is_staff", False)
        kwargs.setdefault("is_superuser", False)

        user = self.__obtain_user_instance(email, full_name, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        full_name: str,
        password: str | None = None,
        **kwargs: Any,
    ) -> CustomUser:
        """Create an active administrator and reject contradictory flags."""
        for flag in ("is_active", "is_staff", "is_superuser"):
            kwargs.setdefault(flag, True)
            if kwargs[flag] is not True:
                raise ValidationError(
                    f"A superuser must have {flag}=True.",
                    code=f"invalid_{flag}",
                )

        return self.create_user(email, full_name, password, **kwargs)


class CustomUser(AbstractBaseUser, PermissionsMixin, AbstractBaseModel):
    """Represent a university account without deriving rights from roles."""

    EMAIL_MAX_LENGTH = 150
    FULL_NAME_MAX_LENGTH = 150
    PASSWORD_MAX_LENGTH = 254
    PHONE_MAX_LENGTH = 30
    IDENTITY_NUMBER_MAX_LENGTH = 50
    ROLE_MAX_LENGTH = 20

    class Role(TextChoices):
        """Describe a user's university role, independently of permissions."""

        STUDENT = "student", "Student"
        TEACHER = "teacher", "Teacher"
        HEADMAN = "headman", "Headman"
        MODERATOR = "moderator", "Moderator"

    email = EmailField(
        verbose_name="Email",
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        db_index=True,
    )
    full_name = CharField(
        verbose_name="Full name",
        max_length=FULL_NAME_MAX_LENGTH,
    )
    password = CharField(
        verbose_name="Password",
        max_length=PASSWORD_MAX_LENGTH,
    )
    phone = CharField(
        verbose_name="Phone",
        max_length=PHONE_MAX_LENGTH,
        blank=True,
    )
    identity_number = CharField(
        verbose_name="Identity number",
        max_length=IDENTITY_NUMBER_MAX_LENGTH,
        blank=True,
    )
    role = CharField(
        verbose_name="Role",
        max_length=ROLE_MAX_LENGTH,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    is_active = BooleanField(
        verbose_name="Active",
        default=True,
    )
    is_staff = BooleanField(
        verbose_name="Staff",
        default=False,
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        """Use readable labels for the user model."""

        verbose_name = "User"
        verbose_name_plural = "Users"

    def get_full_name(self) -> str:
        """Return the account holder's full name."""
        return self.full_name

    def get_short_name(self) -> str:
        """Return the first part of the full name."""
        return self.full_name.split(maxsplit=1)[0] if self.full_name else ""

    def __str__(self) -> str:
        """Identify the account in related-object selectors."""
        return f"{self.full_name} ({self.email})"
