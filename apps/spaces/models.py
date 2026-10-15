from django.core.validators import MinValueValidator
from django.db.models import (
    CASCADE,
    PROTECT,
    BooleanField,
    CharField,
    CheckConstraint,
    ForeignKey,
    IntegerField,
    ManyToManyField,
    PositiveIntegerField,
    Q,
    UniqueConstraint,
)

from apps.abstracts.models import AbstractBaseModel

NAME_MAX_LENGTH = 100
NUMBER_MAX_LENGTH = 20


class Building(AbstractBaseModel):
    """University building that contains rooms"""

    name = CharField(
        verbose_name="Name",
        max_length=NAME_MAX_LENGTH,
        unique=True,
    )

    class Meta:
        verbose_name = "Building"
        verbose_name_plural = "Buildings"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class SpaceType(AbstractBaseModel):
    """Kind of room"""

    name = CharField(
        verbose_name="Name",
        max_length=NAME_MAX_LENGTH,
        unique=True,
    )

    class Meta:
        verbose_name = "Space type"
        verbose_name_plural = "Space types"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Equipment(AbstractBaseModel):
    """Equipment item that can be installed in rooms"""

    name = CharField(
        verbose_name="Name",
        max_length=NAME_MAX_LENGTH,
        unique=True,
    )

    class Meta:
        verbose_name = "Equipment"
        verbose_name_plural = "Equipment"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Space(AbstractBaseModel):
    """Bookable room inside  building"""

    building = ForeignKey(
        to=Building,
        verbose_name="Building",
        on_delete=PROTECT,
        related_name="spaces",
    )
    space_type = ForeignKey(
        to=SpaceType,
        verbose_name="Space type",
        on_delete=PROTECT,
        related_name="spaces",
    )
    name = CharField(
        verbose_name="Name",
        max_length=NAME_MAX_LENGTH,
    )
    number = CharField(
        verbose_name="Number",
        max_length=NUMBER_MAX_LENGTH,
    )
    floor = IntegerField(
        verbose_name="Floor",
    )
    capacity = PositiveIntegerField(
        verbose_name="Capacity",
        validators=[MinValueValidator(1)],
    )
    is_active = BooleanField(
        verbose_name="Is active",
        default=True,
    )
    equipment = ManyToManyField(
        to=Equipment,
        verbose_name="Equipment",
        through="SpaceEquipment",
        related_name="spaces",
        blank=True,
    )

    class Meta:
        verbose_name = "Space"
        verbose_name_plural = "Spaces"
        ordering = ("number",)
        constraints = [
            CheckConstraint(
                condition=Q(capacity__gt=0),
                name="space_capacity_positive",
                violation_error_message="Capacity must be greater than 0",
            ),
            UniqueConstraint(
                fields=("building", "number"),
                name="space_unique_building_number",
                violation_error_message=(
                    "This building already has a room with this number"
                ),
            ),
        ]

    def __str__(self) -> str:
        return f"{self.number} {self.name}"


class SpaceEquipment(AbstractBaseModel):
    """Link table"""

    space = ForeignKey(
        to=Space,
        verbose_name="Space",
        on_delete=CASCADE,
        related_name="equipment_links",
    )
    equipment = ForeignKey(
        to=Equipment,
        verbose_name="Equipment",
        on_delete=PROTECT,
        related_name="space_links",
    )

    class Meta:
        verbose_name = "Space equipment"
        verbose_name_plural = "Space equipment"
        constraints = [
            UniqueConstraint(
                fields=("space", "equipment"),
                name="space_equipment_unique_pair",
                violation_error_message=(
                    "This equipment is already linked to the room"
                ),
            ),
        ]

    def __str__(self) -> str:
        return f"{self.space} - {self.equipment}"
