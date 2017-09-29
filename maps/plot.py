import logging
import math
import os
from collections import namedtuple

import numpy

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib import colors
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import geojsoncontour

from maps.utilgeo import deg2rad, rad2deg
from maps.settings import MAPS_DATA_DIR

logger = logging.getLogger(__name__)

# Make sure the MAPS_DATA_DIR is set in settings.py
assert MAPS_DATA_DIR != ''


def create_or_load_contour_data(observations, config, data_dir, name, do_recreate):
    contour = Contour(observations, config, data_dir=data_dir, name=name)
    if do_recreate or not contour.is_saved:
        contour.create_contour_data()
    else:
        saved_data_valid = contour.load()
        if not saved_data_valid:
            contour.create_contour_data()
    # contour.normalize()
    return contour


def create_contour_levels_linear(Z, n_contours):
    z_max = Z.max()
    z_min = 0.0005*z_max
    # z_mean = Z.mean()
    print('z min: ' + str(z_min))
    # print('z mean: ' + str(z_mean))
    print('z max: ' + str(z_max))
    levels = numpy.logspace(
        start=math.log10(z_min),
        stop=math.log10(0.6*z_max),
        num=n_contours
    )
    norm = colors.LogNorm()
    return levels, norm


def div0( a, b ):
    """ ignore / 0, div0( [-1, 0, 1], 0 ) -> [0, 0, 0] """
    with numpy.errstate(divide='ignore', invalid='ignore'):
        c = numpy.true_divide( a, b )
        c[ ~ numpy.isfinite( c )] = 0  # -inf inf NaN
    return c


def create_contour_plot(observations, config, data_dir=None, name='all', do_recreate=False):
    if data_dir is None:
        data_dir = MAPS_DATA_DIR
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    contour = create_or_load_contour_data(observations, config, data_dir, name, do_recreate)

    contour.create_geojson(data_dir, name, stroke_width=4)


class ContourPlotConfig(object):

    def __init__(self):
        self.lon_start = 3.0
        self.lat_start = 50.5
        self.lon_end = 9.5
        self.lat_end = 53.75
        self.min_angle_between_segments = 7
        Level = namedtuple('Level', 'stepsize_deg sigma n_contours')  # sigma is in [m]
        self.levels = [Level(stepsize_deg=0.002, sigma=500, n_contours=11),
                       Level(stepsize_deg=0.01, sigma=1500, n_contours=9)]


class Contour(object):

    def __init__(self, observations, config, data_dir=None, name='all'):
        logger.info('number of observations: ' + str(len(observations)))
        self.name = name
        self.observations = observations
        self.config = config
        self.data_dir = data_dir
        self.Z = None

    @property
    def contour_data_filepath(self):
        return os.path.join(self.data_dir, 'contour_data_' + self.name + '_' + '.npz')

    @property
    def is_saved(self):
        return os.path.exists(self.contour_data_filepath)

    def load(self):
        logger.info('load: ' + self.contour_data_filepath)
        raise Exception('Not implemented')
        # with open(self.contour_data_filepath, 'rb') as filein:
        #     self.Z = numpy.load(filein)
        # return self.Z.size == self.Z_norm.size

    def save(self):
        with open(self.contour_data_filepath, 'wb') as fileout:
            numpy.save(fileout, self.Z)

    def normalize(self):
        raise Exception('Not implemented')
        # max_val = self.Z.max()
        # min_val = self.Z.min()
        # self.Z_norm = (self.Z - min_val) / (max_val - min_val)

    def create_contour_data(self, filepath=None):
        logger.info('BEGIN')
        numpy.set_printoptions(3, threshold=100, suppress=True)  # .3f

        self.Z = self.get_probability_field()
        self.save()
        logger.info('END')

    def get_probability_field(self):
        logger.info('BEGIN')

        earth_radius = 6360000  # [m], ignore ellipsoid shape

        Z = []
        for level in self.config.levels:
            lat_avg = deg2rad((self.config.lat_start + self.config.lat_end) / 2)  # [rad]
            sigma_lat_deg = rad2deg(level.sigma / earth_radius)  # [deg]
            sigma_lon_deg = rad2deg(level.sigma / (earth_radius * math.cos(lat_avg)))
            # print ("sigma_lat", sigma_lat_deg, "sigma_lon", sigma_lon_deg)

            i_sig = sigma_lat_deg / level.stepsize_deg
            j_sig = sigma_lon_deg / level.stepsize_deg
            i_sig_3 = int(3*i_sig)
            j_sig_3 = int(3*j_sig)
            pdf_factor_lat = 1.0/(math.sqrt(math.pi*(i_sig*i_sig)))
            pdf_factor_lon = 1.0/(math.sqrt(math.pi*(j_sig*j_sig)))
            # print ("i_sig", i_sig, "j_sig", j_sig, "sigma_lat", sigma_lat_deg, "self.config.stepsize_deg", self.config.stepsize_deg)

            latsize = int((self.config.lat_end - self.config.lat_start)/level.stepsize_deg)
            lonsize = int((self.config.lon_end - self.config.lon_start)/level.stepsize_deg)
            z_level = numpy.zeros((latsize, lonsize))
            for obs in self.observations:
                i_obs = (obs.coordinates.lat - self.config.lat_start)/level.stepsize_deg
                j_obs = (obs.coordinates.lon - self.config.lon_start)/level.stepsize_deg
                for i in range(round(i_obs)-i_sig_3, round(i_obs)+i_sig_3):
                    for j in range(round(j_obs)-j_sig_3, round(j_obs)+j_sig_3):
                        try:
                            di = i-i_obs
                            dj = j-j_obs
                            z_level[i][j] += math.exp(-(di*di) / (i_sig * i_sig)) *\
                                             math.exp(-(dj*dj) / (j_sig * j_sig))
                        except IndexError:
                            pass
            Z.append(z_level)
        # Z *= pdf_factor_lat*pdf_factor_lon
        logger.info('END')
        return Z

    def create_geojson(self, data_dir, name, stroke_width=1):
        assert(len(self.Z) == len(self.config.levels))
        for index, z_level in enumerate(self.Z):
            level = self.config.levels[index]
            levels, norm = create_contour_levels_linear(z_level, level.n_contours)
            logger.info('levels: ' + str(levels))

            filepath = os.path.join(data_dir, 'contours_' + name + '_' + str(index) + '_' + '.geojson')
            figure = Figure(frameon=False)
            FigureCanvas(figure)
            ax = figure.add_subplot(111)
            # contours = plt.contourf(lonrange, latrange, Z, levels=levels, cmap=plt.cm.plasma)
            latrange = [self.config.lat_start + i * level.stepsize_deg for i in range(0, z_level.shape[0])]
            lonrange = [self.config.lon_start + i * level.stepsize_deg for i in range(0, z_level.shape[1])]
            contours = ax.contour(
                lonrange, latrange, z_level,
                levels=levels,
                norm=norm,
                cmap=plt.cm.viridis,  # YlGn, magma_r, viridis, inferno, Greens
                linewidths=3
            )

            ndigits = len(str(int(1.0 / level.stepsize_deg))) + 1
            geojsoncontour.contour_to_geojson(
                contour=contours,
                geojson_filepath=filepath,
                contour_levels=levels,
                min_angle_deg=self.config.min_angle_between_segments,
                ndigits=ndigits,
                unit='[<unit here>]',
                stroke_width=stroke_width
            )
