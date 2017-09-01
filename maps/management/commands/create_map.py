import os
import numpy

from matplotlib.colors import LogNorm, SymLogNorm, Normalize

from django.core.management.base import BaseCommand

from observation.models import Observation

from maps.plot import Contour
from maps.plot import ContourPlotConfig

from django.conf import settings


class Command(BaseCommand):
    # def add_arguments(self, parser):
    #     parser.add_argument('--max', type=int, help='The max number of observations to use.', default=None)

    def handle(self, *args, **options):
        N_CONTOURS = 11
        observations = Observation.objects.all()

        config = ContourPlotConfig()

        contour = Contour(observations, config, standard_deviation=2500)

        contour.create_contour_data()

        level_lower = contour.Z.min()
        level_upper = contour.Z.max()

        # level_lower = 0
        # level_upper = 1.0
        print(level_lower)
        print(level_upper)
        # if LOGSCALE:
        #     norm = SymLogNorm(linthresh=1.0, vmin=level_lower, vmax=level_upper)
        #     # norm = PowerNorm(gamma=2, vmin=level_lower, vmax=level_upper)
        #     levels = numpy.logspace(
        #         start=math.log(level_lower, math.e),
        #         stop=math.log(level_upper + 2, math.e),
        #         num=n_contours,
        #         base=math.e
        #     )
        # elif GAUSSCALE:
        #     levels = []
        #     stdev = contour.standard_deviation()
        #     start = -4.0 * stdev
        #     steps = numpy.linspace(start=start, stop=-0.6 * stdev, num=n_contours)
        #     norm_dist = scipy.stats.norm(0, stdev)
        #     for step in steps:
        #         levels.append(norm_dist.pdf(step))
        #     scale_factor = level_upper / levels[-1]
        #     levels = numpy.multiply(levels, scale_factor)
        #     norm = SymLogNorm(linthresh=1.0, vmin=levels[0], vmax=levels[-1])
        #     # norm = PowerNorm(gamma=0.4, vmin=levels[0], vmax=levels[-1])
        # else:
        # norm = SymLogNorm(linthresh=1.0, vmin=level_lower, vmax=level_upper)
        norm = None
        levels = numpy.linspace(
            start=level_lower,
            stop=level_upper,
            num=N_CONTOURS
        )
        print(levels)
        filepath_geojson = os.path.join(settings.STATIC_ROOT, 'data/contours.geojson')
        contour.create_geojson(filepath_geojson, stroke_width=4, levels=levels, norm=norm)
