from django.db.models import DateTimeField, Model
from django.utils import timezone as django_timezone


class AbstractBaseModel(Model):
    """Keep timestamps while leaving marked rows visible to queries."""

    created_at = DateTimeField(
        verbose_name="Created at",
        auto_now_add=True,
    )
    updated_at = DateTimeField(
        verbose_name="Updated at",
        auto_now=True,
    )
    deleted_at = DateTimeField(
        verbose_name="Deleted at",
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    def delete(
        self,
        using: str | None = None,
        keep_parents: bool = False,
    ) -> tuple[int, dict[str, int]]:
        """Mark a saved instance without deleting rows or other fields."""
        if self.pk is None:
            raise ValueError("Cannot delete an unsaved object.")

        self.deleted_at = django_timezone.now()
        self.save(using=using, update_fields=["deleted_at"])
        return 0, {}
