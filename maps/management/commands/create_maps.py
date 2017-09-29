import os
import sys


from django.core.management.base import BaseCommand
from django.utils.text import slugify

from observation.models import Observation
from observation.models import Group
from observation.models import Family
from observation.models import Species

from maps.plot import ContourPlotConfig
from maps.plot import create_contour_plot
from maps.data import observations_to_json

from maps.settings import MAPS_DATA_DIR


class Command(BaseCommand):
    RECREATE = False
    N_CONTOURS = 11
    N_NEAREST = 15
    STANDARD_DEVIATION = 5000

    def add_arguments(self, parser):
        parser.add_argument('--group', type=str, help='', default=None)

    def handle(self, *args, **options):
        group = None
        if options['group'] is not None:
            group = Group.objects.get(slug=slugify(options['group']))
        config_groups = ContourPlotConfig(stepsize_deg=0.01, n_nearest=Command.N_NEAREST)
        observations_all = Observation.objects.filter(coordinates__isnull=False).select_related('coordinates')
        self.create_maps_groups(observations_all, config_groups, group)
        config = ContourPlotConfig(stepsize_deg=0.01, n_nearest=Command.N_NEAREST)
        self.create_maps_families(observations_all, config, group)
        self.create_maps_species(observations_all, config, group)

    @staticmethod
    def create_maps_groups(observations, config, group=None):
        print('create group maps - BEGIN')
        recursionlimit_default = sys.getrecursionlimit()
        print('recursion limit default: ' + str(recursionlimit_default))
        groups = Group.objects.all()
        if group:
            groups = groups.filter(id=group.id)
        sys.setrecursionlimit(10000)
        for group in groups:
            observations_group = observations.filter(group=group)
            Command.create_map(observations_group, config, MAPS_DATA_DIR, group.slug)
        sys.setrecursionlimit(recursionlimit_default)
        print('create group maps - END')

    @staticmethod
    def create_maps_families(observations, config, group=None):
        print('create family maps - BEGIN')
        families = Family.objects.all()
        if group:
            families = families.filter(group=group)
        for family in families:
            observations_fam = observations.filter(family=family)
            data_dir = os.path.join(MAPS_DATA_DIR, family.group.slug)
            Command.create_map(observations_fam, config, data_dir, family.slug)
        print('create family maps - END')

    @staticmethod
    def create_maps_species(observations, config, group=None):
        print('create species maps - BEGIN')
        species = Species.objects.all()
        if group:
            species = species.filter(family__group=group)
        for obj in species:
            observations_species = observations.filter(species=obj)
            data_dir = os.path.join(MAPS_DATA_DIR, obj.family.group.slug, obj.family.slug)
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
        # TODO: remove duplicate code in create_map command
        filepath = os.path.join(data_dir, name + '.json')
        observations_to_json(observations, filepath)
        print('create map - END - ' + str(name))
