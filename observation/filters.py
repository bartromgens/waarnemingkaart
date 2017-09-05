from dal import autocomplete

import django_filters

from observation.models import Observation
from observation.models import Species


class ModelSelect2SlugWidget(autocomplete.ModelSelect2):

    def filter_choices_to_render(self, selected_choices):
        """Override from QuerySetSelectMixin to use the slug instead of pk (pk will change on database reset)"""
        self.choices.queryset = self.choices.queryset.filter(
            slug__in=[c for c in selected_choices if c]
        )


class ObservationFilter(django_filters.FilterSet):
    species = django_filters.ModelChoiceFilter(
        queryset=Species.objects.all(),
        to_field_name='slug',
        method='species_filter',
        label='',
        widget=ModelSelect2SlugWidget(url='species-autocomplete')
    )

    class Meta:
        model = Observation
        exclude = '__all__'

    def species_filter(self, queryset, name, value):
        print('species_filter: ' + str(value))
        return queryset.filter(species=value).distinct()
