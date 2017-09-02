from django.contrib import admin

from observation.models import Observation
from observation.models import Group
from observation.models import Family
from observation.models import Species


class ObservationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'species',
        'family',
        'group',
        'number',
        'datetime',
        'coordinates',
        'waarneming_url',
    )


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'name_nl',
        'name_latin',
        'slug',
    )


class FamilyAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'name_nl',
        'name_latin',
        'slug',
    )


class SpeciesAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'name_nl',
        'name_latin',
        'slug',
    )


admin.site.register(Observation, ObservationAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Family, FamilyAdmin)
admin.site.register(Species, SpeciesAdmin)