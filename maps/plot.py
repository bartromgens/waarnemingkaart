import sys
import os
import math
import logging

import numpy
from scipy.spatial import KDTree

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import geojson
import geojsoncontour

from maps import utilgeo


class ContourPlotConfig(object):

    def __init__(self):
        self.stepsize_deg = 0.02
        self.n_nearest = 20
        self.lon_start = 3.0
        self.lat_start = 50.5
        self.delta_deg = 6.5
        self.lon_end = self.lon_start + self.delta_deg
        self.lat_end = self.lat_start + (self.delta_deg/2.0)
        self.min_angle_between_segments = 7


class Contour(object):

    def __init__(self, observations, config, data_dir=None, standard_deviation=5000):
        print('number of observations: ' + str(len(observations)))
        self.observations = observations
        self.config = config
        self.data_dir = data_dir
        self.standard_deviation = standard_deviation
        self.lonrange = numpy.arange(self.config.lon_start, self.config.lon_end, self.config.stepsize_deg)
        self.latrange = numpy.arange(self.config.lat_start, self.config.lat_end, self.config.stepsize_deg)
        self.Z = numpy.zeros((int(self.lonrange.shape[0]), int(self.latrange.shape[0])))

    def load(self):
        with open('contour_data_' + str(self.standard_deviation) + '.npz', 'rb') as filein:
            self.Z = numpy.load(filein)

    def save(self):
        with open('contour_data_' + str(self.standard_deviation) + '.npz', 'wb') as fileout:
            numpy.save(fileout, self.Z)

    # def get_probability_cone_height(self, volume):
    #     height = (3*volume) / (math.pi*self.standard_deviation*self.standard_deviation)
    #     return height
    #
    # def get_probability_bell_height(self, volume):
    #     height = volume / (2*math.pi*self.standard_deviation*self.standard_deviation)
    #     return height

    def create_contour_data(self, filepath=None):
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
            observation_data.append({'number': observation.number})

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

    def calc_normal_distribution_exponent(self, x_minus_mean):
        return math.exp(-(x_minus_mean * x_minus_mean) / (2 * self.standard_deviation * self.standard_deviation))

    # def standard_deviation(self):
    #     return self.standard_deviation

    def get_probability_field(self, kdtree, observations, gps, latrange, lonrange, altitude, n_nearest):
        Z = numpy.zeros((int(latrange.shape[0]), int(lonrange.shape[0])))

        for i, lat in enumerate(latrange):
            if i % (len(latrange) / 10) == 0:
                print((str(int(i / len(latrange) * 100)) + '%'))
            for j, lon in enumerate(lonrange):
                x, y, z = gps.lla2ecef([lat, lon, altitude])
                local_probability = 0.0
                distances, indexes = kdtree.query([x, y, z], n_nearest)
                for distance, index in zip(distances, indexes):
                    if distance < 1:
                        continue
                    # if distance < Contour.standard_deviation:
                    #     local_emission += (Contour.standard_deviation-distance)*sources[index]['height']/Contour.standard_deviation
                    # local_probability += observations[index]['number'] * self.calc_normal_distribution_exponent(distance)
                    local_probability += 1 * self.calc_normal_distribution_exponent(distance)
                # print('local emission: ' + str(local_emission_per_square_m))
                # print(local_probability)
                Z[i][j] = local_probability
        return Z

    def create_contour_plot(self, levels, norm=None):
        figure = Figure(frameon=False)
        FigureCanvas(figure)
        ax = figure.add_subplot(111)
        # contours = plt.contourf(lonrange, latrange, Z, levels=levels, cmap=plt.cm.plasma)
        contours = ax.contour(
            self.lonrange, self.latrange, self.Z,
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
            cmap=plt.cm.magma_r,
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
