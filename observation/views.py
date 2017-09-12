import urllib.parse

from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import TemplateView

from dal import autocomplete

from observation.models import Observation
from observation.models import Species
from observation.models import Family
from observation.models import Group

from observation.filters import ObservationFilter


class ObservationMapView(TemplateView):
    template_name = 'observation/map.html'

    def dispatch(self, request, *args, **kwargs):
        group_slug = request.GET.get('group')
        family_slug = request.GET.get('family')
        species_slug = request.GET.get('species')
        needs_redirect = False
        if family_slug and species_slug:
            species = Species.objects.get(slug=species_slug)
            family = Family.objects.get(slug=family_slug)
            if species.family.id is not family.id:
                needs_redirect = True
                species_slug = ''
        if species_slug and (not family_slug or not group_slug):
            species = Species.objects.get(slug=species_slug)
            family_slug = species.family.slug
            group_slug = species.family.group.slug
            needs_redirect = True
        if needs_redirect:
            new_args = {
                'group': group_slug,
                'family': family_slug,
                'species': species_slug,
            }
            url = '/?' + urllib.parse.urlencode(new_args)
            return redirect(url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        observation_filter = ObservationFilter(self.request.GET, queryset=Observation.objects.all().order_by('-datetime'))
        group_slug = self.request.GET.get('group')
        family_slug = self.request.GET.get('family')
        species_slug = self.request.GET.get('species')
        page_title = ""
        if species_slug:
            species = Species.objects.get(slug=species_slug)
            context['species'] = species
            page_title += species.name_nl + ' - '
        if family_slug:
            family = Family.objects.get(slug=family_slug)
            context['family'] = family
            page_title += family.name_nl + ' - '
            context['speciess'] = Species.objects.filter(family=family)
        if group_slug:
            group = Group.objects.get(slug=group_slug)
            context['group'] = group
            page_title += group.name_nl
            context['families'] = Family.objects.filter(group=group)
        else:
            context['groups'] = Group.objects.all()
        if not page_title:
            page_title = 'Home'
        context['page_title'] = page_title
        context['filter'] = observation_filter
        return context


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


class Select2QuerySetCustomView(autocomplete.Select2QuerySetView):
    paginate_by = 50


class SpeciesAutocomplete(Select2QuerySetCustomView):
    def get_queryset(self):
        objs = Species.objects.exclude(name_nl='').order_by('name_nl')

        family_slug = self.forwarded.get('family', None)
        if family_slug:
            objs = objs.filter(family__slug=family_slug)

        group_slug = self.forwarded.get('group', None)
        if group_slug:
            objs = objs.filter(family__group__slug=group_slug)

        ids = []
        if self.q:
            for ob in objs:
                if self.q.lower() in ob.name_nl.lower():
                    ids.append(ob.id)
            return Species.objects.filter(pk__in=ids)
        return objs

    def get_result_value(self, result):
        return result.slug


class FamilyAutocomplete(Select2QuerySetCustomView):
    def get_queryset(self):
        objs = Family.objects.exclude(name_nl='').order_by('name_nl')

        group_slug = self.forwarded.get('group', None)
        if group_slug:
            objs = objs.filter(group__slug=group_slug)

        ids = []
        if self.q:
            for ob in objs:
                if self.q.lower() in ob.name_nl.lower():
                    ids.append(ob.id)
            return Family.objects.filter(pk__in=ids)
        return objs

    def get_result_value(self, result):
        return result.slug


class GroupAutocomplete(Select2QuerySetCustomView):
    def get_queryset(self):
        objs = Group.objects.exclude(name_nl='').order_by('name_nl')
        ids = []
        if self.q:
            for ob in objs:
                if self.q.lower() in ob.name_nl.lower():
                    ids.append(ob.id)
            return Group.objects.filter(pk__in=ids)
        return objs

    def get_result_value(self, result):
        return result.slug
