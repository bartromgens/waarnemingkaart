from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import TemplateView

from dal import autocomplete

from observation.models import Observation
from observation.models import Species

from observation.filters import ObservationFilter


class ObservationsView(TemplateView):
    template_name = 'observation/observations.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        observation_filter = ObservationFilter(self.request.GET, queryset=Observation.objects.all().order_by('-datetime'))
        paginator = Paginator(observation_filter.qs, 100)
        page = self.request.GET.get('page')
        try:
            observations = paginator.page(page)
        except PageNotAnInteger:
            observations = paginator.page(1)
        except EmptyPage:
            observations = paginator.page(paginator.num_pages)
        context['observations'] = observations
        context['filter'] = observation_filter
        context['n_results'] = observation_filter.qs.count()
        return context


class SpeciesAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        species = Species.objects.exclude(name_nl='').order_by('name_nl')
        species_ids = []
        if self.q:
            for item in species:
                if self.q.lower() in item.name_nl.lower():
                    species_ids.append(item.id)
            return Species.objects.filter(pk__in=species_ids)
        return species

    def get_result_value(self, result):
        return result.slug
