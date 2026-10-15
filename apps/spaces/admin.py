from django.contrib import admin
from django.db.models import QuerySet
from django.forms.models import BaseInlineFormSet
from django.http import HttpRequest
from unfold.admin import ModelAdmin, TabularInline

from apps.schedules.admin import OpeningHoursInline
from apps.spaces.models import (
    Building,
    Equipment,
    Space,
    SpaceEquipment,
    SpaceType,
)

TIMESTAMP_FIELDS = ("created_at", "updated_at", "deleted_at")


class CatalogAdmin(ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    readonly_fields = TIMESTAMP_FIELDS
    fieldsets = (
        (None, {"fields": ("name",)}),
        ("Dates", {"fields": TIMESTAMP_FIELDS}),
    )

    def has_delete_permission(
        self, request: HttpRequest, obj: object | None = None
    ) -> bool:
        return False


@admin.register(Building)
class BuildingAdmin(CatalogAdmin):
    """Building list with name search"""


@admin.register(SpaceType)
class SpaceTypeAdmin(CatalogAdmin):
    """Room types list with name search"""


@admin.register(Equipment)
class EquipmentAdmin(CatalogAdmin):
    """Equipment list,search is needed for the inline autocomplete"""


class SpaceEquipmentFormSet(BaseInlineFormSet):
    def delete_existing(
        self,
        obj: SpaceEquipment,
        commit: bool = True,
    ) -> None:
        """Remove the link physically so equipment can be added again."""
        if commit:
            SpaceEquipment.objects.filter(pk=obj.pk).delete()


class SpaceEquipmentInline(TabularInline):
    """Edit room equipment on the room page"""

    model = SpaceEquipment
    formset = SpaceEquipmentFormSet
    extra = 0
    fields = ("equipment",)
    autocomplete_fields = ("equipment",)


@admin.register(Space)
class SpaceAdmin(ModelAdmin):
    """Search,filters,autocomplete and equipment inline in rooms"""

    list_display = (
        "number",
        "name",
        "building",
        "space_type",
        "floor",
        "capacity",
        "is_active",
        "equipment_list",
    )
    list_display_links = ("number", "name")
    list_filter = ("building", "space_type", "is_active", "equipment")
    search_fields = ("name", "number")
    autocomplete_fields = ("building", "space_type")
    readonly_fields = TIMESTAMP_FIELDS
    list_select_related = ("building", "space_type")
    inlines = (
        SpaceEquipmentInline,
        OpeningHoursInline,
    )
    fieldsets = (
        ("Location", {"fields": ("building", "number", "floor")}),
        ("Room", {"fields": ("name", "space_type", "capacity", "is_active")}),
        ("Dates", {"fields": TIMESTAMP_FIELDS}),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Space]:
        return super().get_queryset(request).prefetch_related("equipment")

    @admin.display(description="Equipment")
    def equipment_list(self, obj: Space) -> str:
        return ", ".join(item.name for item in obj.equipment.all()) or "-"

    def has_delete_permission(
        self, request: HttpRequest, obj: Space | None = None
    ) -> bool:
        return False
