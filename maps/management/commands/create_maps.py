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
        parser.add_argument('--select', type=str, help='', default=None)
        parser.add_argument('--skip-groups', action='store_true', help='Do not create maps for groups.')
        parser.add_argument('--skip-families', action='store_true', help='Do not create maps for families.')
        parser.add_argument('--skip-species', action='store_true', help='Do not create maps for species.')

    def handle(self, *args, **options):
        species = None
        family = None
        group = None
        if options['select']:
            try:
                group = Group.objects.get(slug=slugify(options['select']))
            except Group.DoesNotExist:
                try:
                    family = Family.objects.get(slug=slugify(options['select']))
                except Family.DoesNotExist:
                    try:
                        species = Species.objects.get(slug=slugify(options['select']))
                    except Species.DoesNotExist:
                        pass
        config = ContourPlotConfig()
        groups = Group.objects.all()
        families = Family.objects.all()
        speciess = Species.objects.all()
        if species:
            groups = [species.family.group]
            families = [species.family]
            speciess = [species]
        elif family:
            groups = [species.family.group]
            families = [species.family]
            speciess = speciess.filter(family=family)
        elif group:
            groups = [group]
            families = families.filter(group=group)
            speciess = speciess.filter(group=group)
        observations = Observation.objects.filter(coordinates__isnull=False).select_related('coordinates')
        if not options['skip_groups']:
            self.create_maps_groups(observations, groups, config)
        if not options['skip_families']:
            self.create_maps_families(observations, families, config)
        if not options['skip_species']:
            self.create_maps_speciess(observations, speciess, config)

    @staticmethod
    def create_maps_groups(observations, groups, config):
        recursionlimit_default = sys.getrecursionlimit()
        sys.setrecursionlimit(10000)
        for group in groups:
            observations_group = observations.filter(group=group)
            create_map(observations_group, config, MAPS_DATA_DIR, group.slug)
        sys.setrecursionlimit(recursionlimit_default)

    @staticmethod
    def create_map_group(observations, config, group):
        observations_group = observations.filter(group=group)
        create_map(observations_group, config, MAPS_DATA_DIR, group.slug)

    @staticmethod
    def create_maps_families(observations, families, config):
        for family in families:
            observations_fam = observations.filter(family=family)
            data_dir = os.path.join(MAPS_DATA_DIR, family.group.slug)
            create_map(observations_fam, config, data_dir, family.slug)

    @staticmethod
    def create_map_family(observations, config, family):
        observations_fam = observations.filter(family=family)
        data_dir = os.path.join(MAPS_DATA_DIR, family.group.slug)
        create_map(observations_fam, config, data_dir, family.slug)

    @staticmethod
    def create_maps_speciess(observations, speciess, config):
        for species in speciess:
            observations_species = observations.filter(species=species)
            data_dir = os.path.join(MAPS_DATA_DIR, species.family.group.slug, species.family.slug)
            create_map(observations_species, config, data_dir, species.slug)

    @staticmethod
    def create_map_species(observations, config, species):
        observations_species = observations.filter(species=species)
        data_dir = os.path.join(MAPS_DATA_DIR, species.family.group.slug, species.family.slug)
        create_map(observations_species, config, data_dir, species.slug)
