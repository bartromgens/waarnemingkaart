import os
import sys


from django.core.management.base import BaseCommand
from django.conf import settings

from observation.models import Observation
from observation.models import Group
from observation.models import Family
from observation.models import Species

from maps.plot import ContourPlotConfig
from maps.plot import create_contour_plot

from django.conf import settings


class Command(BaseCommand):
    RECREATE = False
    N_CONTOURS = 11
    N_NEAREST = 15
    STANDARD_DEVIATION = 5000

    # def add_arguments(self, parser):
        # parser.add_argument('--recreate', type=bool, help='', default=True)

    def handle(self, *args, **options):
        config_groups = ContourPlotConfig(stepsize_deg=0.01, n_nearest=Command.N_NEAREST)
        observations_all = Observation.objects.filter(coordinates__isnull=False).select_related('coordinates')
        self.create_maps_groups(observations_all, config_groups)
        config = ContourPlotConfig(stepsize_deg=0.01, n_nearest=Command.N_NEAREST)
        self.create_maps_families(observations_all, config)
        self.create_maps_species(observations_all, config)

    @staticmethod
    def create_maps_groups(observations, config):
        print('create group maps - BEGIN')
        recursionlimit_default = sys.getrecursionlimit()
        print('recursion limit default: ' + str(recursionlimit_default))
        sys.setrecursionlimit(10000)
        groups = Group.objects.all()
        for group in groups:
            observations_group = observations.filter(group=group)
            data_dir = os.path.join(settings.STATIC_ROOT, 'data/')
            Command.create_map(observations_group, config, data_dir, group.slug)
        sys.setrecursionlimit(recursionlimit_default)
        print('create group maps - END')

    @staticmethod
    def create_maps_families(observations, config):
        print('create family maps - BEGIN')
        families = Family.objects.all()
        for family in families:
            observations_fam = observations.filter(family=family)
            data_dir = os.path.join(settings.STATIC_ROOT, 'data/', family.group.slug)
            Command.create_map(observations_fam, config, data_dir, family.slug)
        print('create family maps - END')

    @staticmethod
    def create_maps_species(observations, config):
        print('create species maps - BEGIN')
        species = Species.objects.all()
        for obj in species:
            observations_species = observations.filter(species=obj)
            data_dir = os.path.join(settings.STATIC_ROOT, 'data/', obj.family.group.slug, obj.family.slug)
            Command.create_map(observations_species, config, data_dir, obj.slug)
        print('create species maps - END')

    @staticmethod
    def create_map(observations, config, data_dir, name):
        print('create map - BEGIN - ' + str(name))
        if observations.count() < 1:
            return
        config.n_nearest = min(Command.N_NEAREST, observations.count())
        create_contour_plot(
            observations=observations,
            config=config,
            data_dir=data_dir,
            name=name,
            do_recreate=Command.RECREATE,
            n_contours=Command.N_CONTOURS,
            standard_deviation=Command.STANDARD_DEVIATION
        )
        print('create map - END - ' + str(name))
