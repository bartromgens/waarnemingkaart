import os
import numpy

from django.core.management.base import BaseCommand

from observation.models import Observation

from maps.plot import Contour
from maps.plot import ContourPlotConfig
from maps.data import observations_to_json

from django.conf import settings


class Command(BaseCommand):
    # def add_arguments(self, parser):
    #     parser.add_argument('--max', type=int, help='The max number of observations to use.', default=None)

    def handle(self, *args, **options):
        observations = Observation.objects.filter(coordinates__isnull=False)
        filepath = os.path.join(settings.STATIC_ROOT, 'data/observations.json')
        print(filepath)
        observations_to_json(observations, filepath)
