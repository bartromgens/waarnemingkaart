import sys
import os
import math
import logging

import numpy
import scipy.stats
from scipy.spatial import KDTree

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import geojsoncontour

from maps import utilgeo
from maps.settings import MAPS_DATA_DIR

# Make sure the MAPS_DATA_DIR is set in settings.py
assert MAPS_DATA_DIR != ''


STANDAARD_DEVIATION_M = 5000


def load_contour_all(observations, config, data_dir):
    contour = Contour(observations, config, data_dir=data_dir, standard_deviation=STANDAARD_DEVIATION_M, name='all')
    contour.load()
    return contour


def normalize(array_in):
    max_val = max(array_in)
    min_val = min(array_in)
    array_out = []
    for value in array_in:
        array_out.append((value - min_val) / (max_val - min_val))
    return array_out


def load_contour_data_all(config, standard_deviation, name='vogels'):
    contour = Contour([], config, data_dir=MAPS_DATA_DIR, standard_deviation=standard_deviation, name=name)
    contour.load()
    contour.normalize()
    return contour


def create_or_load_contour_data(observations, config, data_dir, name, do_recreate, standard_deviation):
    contour = Contour(observations, config, data_dir=data_dir, standard_deviation=standard_deviation, name=name)

    if do_recreate or not contour.is_saved:
        contour.create_contour_data()
    else:
        saved_data_valid = contour.load()
        if not saved_data_valid:
            contour.create_contour_data()
    contour.normalize()
    return contour


def create_contour_levels(contour, n_contours):
    start = 1.8 * contour.standard_deviation
    stop = 0.3 * contour.standard_deviation
    steps = numpy.linspace(start=start, stop=stop, num=n_contours)

    levels = []
    for step in steps:
        levels.append(contour.calc_normal_pdf(step))
    # for i in range(0, len(levels)-1):
    #     diff = levels[i+1]-levels[i]
    #     print(diff)
    # levels = normalize(levels)
    return levels


def div0( a, b ):
    """ ignore / 0, div0( [-1, 0, 1], 0 ) -> [0, 0, 0] """
    with numpy.errstate(divide='ignore', invalid='ignore'):
        c = numpy.true_divide( a, b )
        c[ ~ numpy.isfinite( c )] = 0  # -inf inf NaN
    return c


def create_contour_plot(observations, config, data_dir=None, name='all', do_recreate=False, n_contours=11, standard_deviation=STANDAARD_DEVIATION_M):
    if data_dir is None:
        data_dir = MAPS_DATA_DIR
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    filepath_geojson = os.path.join(data_dir, 'contours_' + name + '.geojson')

    contour = create_or_load_contour_data(observations, config, data_dir, name, do_recreate, standard_deviation)

    levels = create_contour_levels(contour, n_contours)

    print('Z.max(): ' + str(contour.Z.max()))
    print('Z.min(): ' + str(contour.Z.min()))
    print('levels: ' + str(levels))

    contour.create_geojson(filepath_geojson, stroke_width=4, levels=levels, norm=None)


class ContourPlotConfig(object):

    def __init__(self, stepsize_deg=0.01, n_nearest=30):
        self.stepsize_deg = stepsize_deg
        self.n_nearest = n_nearest
        self.lon_start = 3.0
        self.lat_start = 50.5
        self.delta_deg = 6.5
        self.lon_end = self.lon_start + self.delta_deg
        self.lat_end = self.lat_start + (self.delta_deg/2.0)
        self.min_angle_between_segments = 7


class Contour(object):

    def __init__(self, observations, config, data_dir=None, standard_deviation=5000, name='all'):
        print('number of observations: ' + str(len(observations)))
        self.name = name
        self.observations = observations
        self.config = config
        self.data_dir = data_dir
        self.standard_deviation = standard_deviation
        self.lonrange = numpy.arange(self.config.lon_start, self.config.lon_end, self.config.stepsize_deg)
        self.latrange = numpy.arange(self.config.lat_start, self.config.lat_end, self.config.stepsize_deg)
        self.Z = numpy.zeros((int(self.lonrange.shape[0]), int(self.latrange.shape[0])))
        self.variance_x2 = (2.0 * self.standard_deviation * self.standard_deviation)
        self.pdf_factor = 1.0/(math.sqrt(math.pi*self.variance_x2))
        self.Z_norm = numpy.zeros((int(self.lonrange.shape[0]), int(self.latrange.shape[0])))
        # self.pdf_factor = 1.0

    @property
    def contour_data_filepath(self):
        return os.path.join(self.data_dir, 'contour_data_' + self.name + '_' + str(self.standard_deviation) + '.npz')

    @property
    def is_saved(self):
        return os.path.exists(self.contour_data_filepath)

    def load(self):
        print('load: ' + self.contour_data_filepath)
        with open(self.contour_data_filepath, 'rb') as filein:
            self.Z = numpy.load(filein)
        return self.Z.size == self.Z_norm.size

    def save(self):
        with open(self.contour_data_filepath, 'wb') as fileout:
            numpy.save(fileout, self.Z)

    def normalize(self):
        max_val = self.Z.max()
        min_val = self.Z.min()
        self.Z_norm = (self.Z - min_val) / (max_val - min_val)

    def create_contour_data(self, filepath=None):
        print('create_contour_data - BEGIN')
        numpy.set_printoptions(3, threshold=100, suppress=True)  # .3f
        altitude = 0.0

        gps = utilgeo.GPS()

        positions = []
        observation_data = []
        for observation in self.observations:
            if observation.coordinates is None:
                continue
            # height = self.get_probability_cone_height(observation.number)
            x, y, z = gps.lla2ecef([observation.coordinates.lat, observation.coordinates.lon, altitude])
            positions.append([x, y, z])
            observation_data.append({'number': observation.number}) #, 'lat': observation.coordinates.lat, 'lon': observation.coordinates.lon})

        tree = KDTree(positions)

        self.Z = self.get_probability_field(
            kdtree=tree,
            observations=observation_data,
            gps=gps,
            lonrange=self.lonrange,
            latrange=self.latrange,
            altitude=altitude,
            n_nearest=min([self.config.n_nearest, len(self.observations)])
        )
        self.save()
        print('create_contour_data - END')

    def calc_normal_pdf(self, x_minus_mean):
        return self.pdf_factor * math.exp(-(x_minus_mean * x_minus_mean) / self.variance_x2)

    def get_probability_field(self, kdtree, observations, gps, latrange, lonrange, altitude, n_nearest):
        Z = numpy.zeros((int(latrange.shape[0]), int(lonrange.shape[0])))

        for i, lat in enumerate(latrange):
            if i % round((len(latrange) / 20)) == 0:
                print((str(int(i / len(latrange) * 100)) + '%'))

            for j, lon in enumerate(lonrange):
                x, y, z = gps.lla2ecef([lat, lon, altitude])
                distances, indexes = kdtree.query([x, y, z], n_nearest)
                if isinstance(distances, float):
                    distances = [distances]
                    indexes = [indexes]
                local_probability = 0.0
                weights_sum = 0
                for distance, index in zip(distances, indexes):
                    local_probability += self.calc_normal_pdf(distance) / distance  #* observations[index]['number']
                    weights_sum += 1/distance
                Z[i][j] = local_probability/weights_sum  # see https://en.wikipedia.org/wiki/Mixture_distribution
        return Z

    def create_contour_plot(self, levels, norm=None):
        figure = Figure(frameon=False)
        FigureCanvas(figure)
        ax = figure.add_subplot(111)
        # contours = plt.contourf(lonrange, latrange, Z, levels=levels, cmap=plt.cm.plasma)
        contours = ax.contour(
            self.lonrange, self.latrange, self.Z_norm,
            levels=levels,
            norm=norm,
            cmap=plt.cm.jet,
            linewidths=3
        )
        figure.savefig('test.png', dpi=90)

    def create_geojson(self, filepath, stroke_width=1, levels=(), norm=None):
        figure = Figure(frameon=False)
        FigureCanvas(figure)
        ax = figure.add_subplot(111)
        # contours = plt.contourf(lonrange, latrange, Z, levels=levels, cmap=plt.cm.plasma)
        contours = ax.contour(
            self.lonrange, self.latrange, self.Z,
            levels=levels,
            norm=norm,
            cmap=plt.cm.viridis,  # YlGn, magma_r, viridis, inferno, Greens
            linewidths=3
        )

        ndigits = len(str(int(1.0 / self.config.stepsize_deg))) + 1
        geojsoncontour.contour_to_geojson(
            contour=contours,
            geojson_filepath=filepath,
            contour_levels=levels,
            min_angle_deg=self.config.min_angle_between_segments,
            ndigits=ndigits,
            unit='[<unit here>]',
            stroke_width=stroke_width
        )
