import os
import sys


from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings

from observation.models import Observation
from observation.models import Group
from observation.models import Family
from observation.models import Species

from maps.plot import ContourPlotConfig
from maps.plot import create_contour_plot
from maps.data import observations_to_json

from maps.settings import MAPS_DATA_DIR


class Command(BaseCommand):
    RECREATE = True

    def add_arguments(self, parser):
        parser.add_argument('--species', type=str, help='', default="grutto")
        parser.add_argument('--fast', action='store_true', help='Use a lower spatial resolution to increase speed. Use for testing.')
        # parser.add_argument('--recreate', type=bool, help='', default=False)

    def handle(self, *args, **options):
        species_name = options['species']
        observations_all = Observation.objects.filter(coordinates__isnull=False).select_related('coordinates')
        config = ContourPlotConfig()
        species = Species.objects.get(slug=slugify(species_name))
        self.create_map_species(observations_all, config, species)

    @staticmethod
    def create_map_species(observations, config, species):
        print('create species map - BEGIN')
        observations_species = observations.filter(species=species)
        data_dir = os.path.join(MAPS_DATA_DIR, species.family.group.slug, species.family.slug)
        Command.create_map(observations_species, config, data_dir, species.slug)
        print('create species map - END')

    @staticmethod
    def create_map(observations, config, data_dir, name):
        print('create map - BEGIN - ' + str(name))
        if observations.count() < 1:
            return
        create_contour_plot(
            observations=observations,
            config=config,
            data_dir=data_dir,
            name=name,
            do_recreate=Command.RECREATE
        )
        filepath = os.path.join(data_dir, name + '.json')
        observations_to_json(observations, filepath)
        print('create map - END - ' + str(name))
