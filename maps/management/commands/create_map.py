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
        species_slug = "grutto"
        observations_all = Observation.objects.all().select_related('coordinates')
        config = ContourPlotConfig(stepsize_deg=0.02, n_nearest=Command.N_NEAREST)
        species = Species.objects.get(slug=species_slug)
        self.create_map_species(observations_all, config, species)

    @staticmethod
    def create_map_species(observations, config, species):
        print('create species map - BEGIN')
        observations_species = observations.filter(species=species)
        data_dir = os.path.join(settings.STATIC_ROOT, 'data/', species.family.group.slug, species.family.slug)
        Command.create_map(observations_species, config, data_dir, species.slug)
        print('create species map - END')

    @staticmethod
    def create_map(observations, config, data_dir, name):
        print('create map - BEGIN')
        print(name)
        if observations.count() < 10:
            return
        config.n_nearest = min(Command.N_NEAREST, observations.count() - 1)
        create_contour_plot(
            observations=observations,
            config=config,
            data_dir=data_dir,
            name=name,
            do_recreate=Command.RECREATE,
            n_contours=Command.N_CONTOURS,
            standard_deviation=Command.STANDARD_DEVIATION
        )
        print('create map - END')
