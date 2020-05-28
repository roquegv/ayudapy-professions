from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from oficios.models import Oficio


def unresolve(modeladmin, request, queryset):
    queryset.update(resolved=False)


def resolve(modeladmin, request, queryset):
    queryset.update(resolved=True)


def deactivate(modeladmin, request, queryset):
    queryset.update(active=False)


def activate(modeladmin, request, queryset):
    queryset.update(active=True)

resolve.short_description = "Marcar oficios seleccionadas como resueltas"
unresolve.short_description = "Marcar oficios seleccionadas como NO resueltas"
deactivate.short_description = "Marcar oficios seleccionadas como inactivas"
activate.short_description = "Marcar oficios seleccionadas como activas"

# Register your models here.
class OficioAdmin(LeafletGeoAdmin):
    list_display = (
        "__str__",
        "id",
        "name",
        "phone",
        "resolved",
        "active",
        "title",
        "message",
        "upvotes",
        "downvotes",
    )
    search_fields = ["title", "message", "name", "phone"]
    actions = [resolve, unresolve, deactivate, activate]

admin.site.register(Oficio, OficioAdmin)