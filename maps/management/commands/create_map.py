import os
import numpy
import scipy.stats

from matplotlib.colors import LogNorm, SymLogNorm, Normalize

from django.core.management.base import BaseCommand
from django.conf import settings

from observation.models import Observation
from observation.models import Family

from maps.plot import Contour
from maps.plot import ContourPlotConfig
from maps.plot import create_contour_plot

from django.conf import settings


class Command(BaseCommand):
    # def add_arguments(self, parser):
    #     parser.add_argument('--max', type=int, help='The max number of observations to use.', default=None)

    def handle(self, *args, **options):
        RECREATE = True
        N_CONTOURS = 11
        config = ContourPlotConfig(stepsize_deg=0.01)
        observations_all = Observation.objects.all().select_related('coordinates')
        create_contour_plot(
            observations=observations_all,
            config=config,
            name='all',
            do_recreate=RECREATE,
            n_contours=N_CONTOURS,
            standard_deviation=4000
        )
