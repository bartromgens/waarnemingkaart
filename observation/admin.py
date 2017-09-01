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
        'url',
    )


admin.site.register(Observation, ObservationAdmin)