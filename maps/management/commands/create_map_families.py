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
from maps.plot import load_contour_all

from django.conf import settings


class Command(BaseCommand):
    # def add_arguments(self, parser):
    #     parser.add_argument('--max', type=int, help='The max number of observations to use.', default=None)

    def handle(self, *args, **options):
        RECREATE = True
        N_CONTOURS = 15
        config = ContourPlotConfig(stepsize_deg=0.02)
        observations_all = Observation.objects.all().select_related('coordinates')

        # data_dir = os.path.join(settings.STATIC_ROOT, 'data/')
        # contour_all = load_contour_all(observations=observations_all, config=config, data_dir=data_dir)
        # contour_all.normalize()

        families = Family.objects.all()
        for family in families:
            print(family)
            observations = observations_all.filter(family=family.id)
            if observations.count() > 100:
                create_contour_plot(
                    observations=observations,
                    config=config,
                    name=family.slug,
                    do_recreate=RECREATE,
                    n_contours=N_CONTOURS,
                )
