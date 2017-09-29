import logging
import os

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from observation.models import Observation
from observation.models import Species

from maps.plot import ContourPlotConfig
from maps.plot import create_map

from maps.settings import MAPS_DATA_DIR

logger = logging.getLogger(__name__)


class Command(BaseCommand):

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
        logger.info('BEGIN: ' + species)
        observations_species = observations.filter(species=species)
        data_dir = os.path.join(MAPS_DATA_DIR, species.family.group.slug, species.family.slug)
        create_map(observations_species, config, data_dir, species.slug)
        logger.info('END:' + species)
