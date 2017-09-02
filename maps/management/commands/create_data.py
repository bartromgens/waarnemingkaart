import os
import numpy

from django.core.management.base import BaseCommand

from observation.models import Observation
from observation.models import Family

from maps.plot import Contour
from maps.plot import ContourPlotConfig
from maps.data import observations_to_json

from django.conf import settings


class Command(BaseCommand):
    # def add_arguments(self, parser):
    #     parser.add_argument('--max', type=int, help='The max number of observations to use.', default=None)

    def handle(self, *args, **options):
        observations_all = Observation.objects.filter(coordinates__isnull=False)
        # meeuw_family = Family.objects.get(name_nl='Meeuwen, Sterns en Schaarbekken')
        # observations = observations.filter(family=meeuw_family)
        families = Family.objects.all()
        for family in families:
            print(family)
            observations = observations_all.filter(family=family.id)
            filepath = os.path.join(settings.STATIC_ROOT, 'data/observations_' + family.slug + '.json')
            print(filepath)
            observations_to_json(observations, filepath)
