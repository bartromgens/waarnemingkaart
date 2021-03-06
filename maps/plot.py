import logging
import math
import os
import time

import numpy

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib import colors
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import geojsoncontour

from maps.utilgeo import deg2rad, rad2deg
from maps.settings import MAPS_DATA_DIR
from maps.data import observations_to_json, highlights_to_json

from maps.modules.density import calc_field

logger = logging.getLogger(__name__)

# Make sure the MAPS_DATA_DIR is set in settings.py
assert MAPS_DATA_DIR != ''


class Highlight(object):

    def __init__(self, dens_frac=0, species=None, lat=0.0, lon=0.0):
        self.dens_frac = dens_frac
        self.species = species
        self.lat = lat
        self.lon = lon


class HighlightMap(object):

    def __init__(self, config):
        x_range = range(config.latsize(config.levels[0]))
        y_range = range(config.lonsize(config.levels[0]))
        self.map = [[Highlight() for y in y_range] for x in x_range]


def create_map(observations, config, data_dir, name):
    logger.info('BEGIN - ' + str(name))
    if observations.count() < 1:
        return

    if data_dir is None:
        data_dir = MAPS_DATA_DIR
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    contour = Contour(observations, config, data_dir=data_dir, name=name)
    contour.create_contour_data()
    contour.create_geojson(data_dir, name, stroke_width=4)

    observations_filepath = os.path.join(data_dir, name + '.json')
    observations_to_json(observations, observations_filepath)

    logger.info('END - ' + str(name))
    return contour.Z


def create_map_for_species(observations, config, data_dir, species, highlight_map):
    if not observations:
        logger.warning('no observations for {}'.format(species.slug))
        return
    Z = create_map(observations, config, data_dir, species.slug)
    z_level = Z[0]
    dens_avg = z_level.mean()
    for x in range(0, z_level.shape[0]):
        for y in range(0, z_level.shape[1]):
            dens_frac = z_level[x][y] / dens_avg
            if highlight_map.map[x][y].dens_frac < dens_frac:
                lat = config.lat_start + x * config.levels[0].stepsize_deg
                lon = config.lon_start + y * config.levels[0].stepsize_deg
                highlight_map.map[x][y] = Highlight(dens_frac, species, lat, lon)


def create_highlights(highlight_map, data_dir):
    highlights_filepath = os.path.join(data_dir, 'highlights.json')
    highlights_to_json(highlight_map, highlights_filepath)


class Level(object):

    def __init__(self, stepsize_deg, sigma, n_contours):
        self.stepsize_deg = stepsize_deg
        self.sigma = sigma  # sigma is in [m]
        self.n_contours = n_contours


class ContourPlotConfig(object):

    def __init__(self):
        self.lon_start = 3.0
        self.lat_start = 50.5
        self.lon_end = 9.5
        self.lat_end = 53.75
        self.min_angle_between_segments = 7
        self.levels = [
            Level(stepsize_deg=0.002, sigma=500, n_contours=11),
            Level(stepsize_deg=0.005, sigma=1500, n_contours=9),
        ]

    def latsize(self, level):
        return int((self.lat_end - self.lat_start)/level.stepsize_deg)

    def lonsize(self, level):
        return int((self.lon_end - self.lon_start)/level.stepsize_deg)


class Contour(object):

    def __init__(self, observations, config, data_dir=None, name='all'):
        logger.info('number of observations: ' + str(len(observations)))
        self.name = name
        self.observations = observations
        self.config = config
        self.data_dir = data_dir
        self.Z = []

    @property
    def contour_data_filepath(self):
        return os.path.join(self.data_dir, 'contour_data_' + self.name + '_' + '.npz')

    def create_contour_data(self):
        logger.info('BEGIN')
        numpy.set_printoptions(3, threshold=100, suppress=True)  # .3f
        self.Z = self.get_probability_field()
        logger.info('END')

    def get_probability_field(self):
        logger.info('BEGIN')
        start = time.time()
        earth_radius = 6360000  # [m], ignore ellipsoid shape
        Z = []
        for level in self.config.levels:
            lat_avg = deg2rad((self.config.lat_start + self.config.lat_end) / 2)  # [rad]
            sigma_lat_deg = rad2deg(level.sigma / earth_radius)  # [deg]
            sigma_lon_deg = rad2deg(level.sigma / (earth_radius * math.cos(lat_avg)))
            i_sig = sigma_lat_deg / level.stepsize_deg
            j_sig = sigma_lon_deg / level.stepsize_deg
            # pdf_factor_lat = 1.0/(math.sqrt(math.pi*(i_sig*i_sig)))
            # pdf_factor_lon = 1.0/(math.sqrt(math.pi*(j_sig*j_sig)))
            grid_obs = []
            for obs in self.observations:
                obs_x = (obs.coordinates.lat - self.config.lat_start)/level.stepsize_deg
                obs_y = (obs.coordinates.lon - self.config.lon_start)/level.stepsize_deg
                grid_obs.append([obs_x, obs_y])
            latsize = self.config.latsize(level)
            lonsize = self.config.lonsize(level)
            densities = calc_field(grid_obs, latsize, lonsize, i_sig, j_sig)
            z_level = numpy.array(densities)
            Z.append(z_level)
        # Z *= pdf_factor_lat*pdf_factor_lon
        end = time.time()
        logger.info('END - time: ' + str(end - start))
        return Z

    def create_geojson(self, data_dir, name, stroke_width=1):
        logger.info('BEGIN')
        start = time.time()
        assert(len(self.Z) == len(self.config.levels))
        for index, z_level in enumerate(self.Z):
            level = self.config.levels[index]
            levels, norm = self.create_contour_levels(z_level, level.n_contours)
            # logger.info('levels: ' + str(levels))

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
        end = time.time()
        logger.info('END - time: ' + str(end - start))

    @staticmethod
    def create_contour_levels(Z, n_contours):
        z_max = Z.max()
        if z_max == 0:
            z_max = 1

        z_min = 0.0005*z_max
        # logger.info('z min: ' + str(z_min))
        # logger.info('z max: ' + str(z_max))
        levels = numpy.logspace(
            start=math.log10(z_min),
            stop=math.log10(0.6*z_max),
            num=n_contours
        )
        norm = colors.LogNorm()
        return levels, norm
