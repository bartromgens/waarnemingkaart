import os
import numpy

from django.core.management.base import BaseCommand

from observation.models import Observation
from observation.models import Group
from observation.models import Family
from observation.models import Species

from maps.data import observations_to_json

from maps.settings import MAPS_DATA_DIR


class Command(BaseCommand):
    # def add_arguments(self, parser):
    #     parser.add_argument('--max', type=int, help='The max number of observations to use.', default=None)

    def handle(self, *args, **options):
        observations_all = Observation.objects.filter(coordinates__isnull=False)
        # meeuw_family = Family.objects.get(name_nl='Meeuwen, Sterns en Schaarbekken')
        # observations = observations.filter(family=meeuw_family)

        groups = Group.objects.all()
        for group in groups:
            print(group)
            observations = observations_all.filter(group=group)
            data_dir = os.path.join(MAPS_DATA_DIR)
            filepath = os.path.join(MAPS_DATA_DIR, group.slug + '.json')
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            print(filepath)
            observations_to_json(observations, filepath)

        families = Family.objects.all()
        for family in families:
            print(family)
            observations = observations_all.filter(family=family)
            data_dir = os.path.join(MAPS_DATA_DIR, family.group.slug)
            filepath = os.path.join(data_dir, family.slug + '.json')
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            print(filepath)
            observations_to_json(observations, filepath)

        species = Species.objects.all()
        for obj in species:
            print(obj)
            observations = observations_all.filter(species=obj)
            data_dir = os.path.join(MAPS_DATA_DIR, obj.family.group.slug, obj.family.slug)
            filepath = os.path.join(data_dir, obj.slug + '.json')
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            print(filepath)
            observations_to_json(observations, filepath)