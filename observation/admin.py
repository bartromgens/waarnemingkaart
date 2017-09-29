from django.contrib import admin

from observation.models import Observation
from observation.models import Group
from observation.models import Family
from observation.models import Species

from observation.models import BioClassObservationStats


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
    list_filter = ('group', 'family')


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'name_nl',
        'name_latin',
        'slug',
        'n_observations',
    )


class FamilyAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'group',
        'name',
        'name_nl',
        'name_latin',
        'slug',
        'n_observations',
    )
    list_filter = ('group',)


class SpeciesAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'family',
        'name',
        'name_nl',
        'name_latin',
        'slug',
        'n_observations',
    )
    list_filter = ('family__group', 'family')


class BioClassObservationStatsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'group',
        'family',
        'species',
        'n_observations',
    )


admin.site.register(Observation, ObservationAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Family, FamilyAdmin)
admin.site.register(Species, SpeciesAdmin)
admin.site.register(BioClassObservationStats, BioClassObservationStatsAdmin)