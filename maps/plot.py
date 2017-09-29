import sys
import os
import math
import logging

import numpy

import scipy.stats
from scipy.spatial import KDTree

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib import colors
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import geojsoncontour

from maps import utilgeo
from maps.utilgeo import deg2rad, rad2deg
from math import cos
from maps.settings import MAPS_DATA_DIR

# Make sure the MAPS_DATA_DIR is set in settings.py
assert MAPS_DATA_DIR != ''


STANDAARD_DEVIATION_M = 5000



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


def create_contour_levels_linear(Z, n_contours):
    z_max = Z.max()
    z_min = 0.01*z_max
    # z_mean = Z.mean()
    print('z min: ' + str(z_min))
    # print('z mean: ' + str(z_mean))
    print('z max: ' + str(z_max))
    levels = numpy.logspace(
        start=math.log10(z_min),
        stop=math.log10(0.9*z_max),
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


def create_contour_plot(observations, config, data_dir=None, name='all', do_recreate=False, n_contours=11, standard_deviation=STANDAARD_DEVIATION_M):
    if data_dir is None:
        data_dir = MAPS_DATA_DIR
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    filepath_geojson = os.path.join(data_dir, 'contours_' + name + '.geojson')

    contour = create_or_load_contour_data(observations, config, data_dir, name, do_recreate, standard_deviation)

    levels, norm = create_contour_levels_linear(contour.Z, n_contours)
    print('levels: ' + str(levels))

    contour.create_geojson(filepath_geojson, stroke_width=4, levels=levels, norm=norm)


class ContourPlotConfig(object):

    def __init__(self, stepsize_deg=0.005, n_nearest=30):
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

        self.Z = self.get_probability_field(
            lonrange=self.lonrange,
            latrange=self.latrange
        )
        self.save()
        print('create_contour_data - END')

    def calc_normal_pdf(self, x_minus_mean):
        return self.pdf_factor * math.exp(-(x_minus_mean * x_minus_mean) / self.variance_x2)

    def get_probability_field(self, latrange, lonrange):
        sigma = 3000  # [m] mobility of species
        earth_radius = 6360000  # [m], ignore ellipsoid shape

        lat_avg = deg2rad((self.config.lat_start + self.config.lat_end) / 2)  # [rad]
        sigma_lat_deg = rad2deg(sigma / earth_radius)  # [deg]
        sigma_lon_deg = rad2deg(sigma / (earth_radius * cos(lat_avg)))
        # print ("sigma_lat", sigma_lat_deg, "sigma_lon", sigma_lon_deg)

        i_sig = sigma_lat_deg / self.config.stepsize_deg
        j_sig = sigma_lon_deg / self.config.stepsize_deg
        i_sig_3 = int(3*i_sig)
        j_sig_3 = int(3*j_sig)
        pdf_factor_lat = 1.0/(math.sqrt(math.pi*(i_sig*i_sig)))
        pdf_factor_lon = 1.0/(math.sqrt(math.pi*(j_sig*j_sig)))
        # print ("i_sig", i_sig, "j_sig", j_sig, "sigma_lat", sigma_lat_deg, "self.config.stepsize_deg", self.config.stepsize_deg)

        Z = numpy.zeros((int(latrange.shape[0]), int(lonrange.shape[0])))
        for obs in self.observations:
            i = int((obs.coordinates.lat - self.config.lat_start) / self.config.stepsize_deg)
            j = int((obs.coordinates.lon - self.config.lon_start) / self.config.stepsize_deg)
            for di in range(-i_sig_3, i_sig_3):
                for dj in range(-j_sig_3, j_sig_3):
                    # print(i, di, j, dj)
                    Z[i + di][j + dj] += pdf_factor_lat * math.exp(-(di * di) / (i_sig * i_sig)) *\
                                         pdf_factor_lon * math.exp(-(dj * dj) / (j_sig * j_sig))
                    # print(Z[i + di][j + dj])
        return Z

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
