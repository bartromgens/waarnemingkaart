import logging
import os
import sys


from django.core.management.base import BaseCommand
from django.utils.text import slugify

from observation.models import Observation
from observation.models import Group
from observation.models import Family
from observation.models import Species

from maps.plot import ContourPlotConfig
from maps.plot import create_map

from maps.settings import MAPS_DATA_DIR

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--group', type=str, help='', default=None)
        parser.add_argument('--skip-groups', action='store_true', help='Do not create maps for groups.')
        parser.add_argument('--skip-families', action='store_true', help='Do not create maps for families.')
        parser.add_argument('--skip-species', action='store_true', help='Do not create maps for species.')

    def handle(self, *args, **options):
        group = None
        if options['group'] is not None:
            group = Group.objects.get(slug=slugify(options['group']))
        config = ContourPlotConfig()
        observations_all = Observation.objects.filter(coordinates__isnull=False).select_related('coordinates')
        if not options['skip_groups']:
            self.create_maps_groups(observations_all, config, group)
        if not options['skip_families']:
            self.create_maps_families(observations_all, config, group)
        if not options['skip_species']:
            self.create_maps_species(observations_all, config, group)

    @staticmethod
    def create_maps_groups(observations, config, group=None):
        logger.info('BEGIN')
        recursionlimit_default = sys.getrecursionlimit()
        logger.info('recursion limit default: ' + str(recursionlimit_default))
        groups = Group.objects.all()
        if group:
            groups = groups.filter(id=group.id)
        sys.setrecursionlimit(10000)
        for group in groups:
            observations_group = observations.filter(group=group)
            create_map(observations_group, config, MAPS_DATA_DIR, group.slug)
        sys.setrecursionlimit(recursionlimit_default)
        logger.info('END')

    @staticmethod
    def create_maps_families(observations, config, group=None):
        logger.info('BEGIN')
        families = Family.objects.all()
        if group:
            families = families.filter(group=group)
        for family in families:
            observations_fam = observations.filter(family=family)
            data_dir = os.path.join(MAPS_DATA_DIR, family.group.slug)
            create_map(observations_fam, config, data_dir, family.slug)
        logger.info('END')

    @staticmethod
    def create_maps_species(observations, config, group=None):
        logger.info('BEGIN')
        species = Species.objects.all()
        if group:
            species = species.filter(family__group=group)
        for obj in species:
            observations_species = observations.filter(species=obj)
            data_dir = os.path.join(MAPS_DATA_DIR, obj.family.group.slug, obj.family.slug)
            create_map(observations_species, config, data_dir, obj.slug)
        logger.info('END')
