import logging
import datetime

import numpy as np

from django.utils import timezone
from plotly.offline import plot
from plotly import tools
from plotly.graph_objs import Layout, Bar, Histogram, Histogram2d, Scatter, XAxis, Margin

logger = logging.getLogger(__name__)

COLOR_PRIMARY = '#26ad81'
COLOR_INFO = '#1d8362'
COLOR_SUCCESS = '#3fad46'
COLOR_WARNING = '#f0ad4e'
COLOR_DANGER = '#d9534f'


class Plot(object):
    plot_title = None

    def __init__(self):
        super().__init__()
        logger.info('create plot')

    def create_data(self):
        raise NotImplementedError

    def create_layout(self):
        raise NotImplementedError

    def create_plot(self):
        logger.info('BEGIN')
        plot_data = self.create_data()
        assert isinstance(plot_data, list)
        plot_layout = self.create_layout()
        assert plot_layout is not None
        plot_config = self.create_plot_config(plot_data, plot_layout)
        assert plot_config is not None
        logger.info('END')
        return Plot.create_plot_html_default(plot_config)

    @staticmethod
    def create_plot_config(data, layout):
        return {"data": data, "layout": layout}

    @staticmethod
    def create_plot_html_default(figure_or_data):
        return plot(
            figure_or_data=figure_or_data,
            show_link=False,
            output_type='div',
            include_plotlyjs=False,
            auto_open=False,
        )


class PlotObservationsVsTime(Plot):

    def __init__(self, observation_dates):
        super().__init__()
        self.observation_dates = observation_dates

    def create_data(self):
        hist_data = Histogram(
            x=self.observation_dates,
            autobinx=False,
            xbins=dict(
                start=(timezone.now() - datetime.timedelta(days=7 * 365)).timestamp() * 1000,
                end=timezone.now().timestamp() * 1000,
                size=60 * 60 * 24 * 7 * 1000
            ),
            marker=dict(
                color=COLOR_PRIMARY,
                line=dict(
                    color=COLOR_INFO,
                    width=1,
                )
            ),
            name='waarnemingen per week',
        )

        return [hist_data]

    def create_layout(self):
        return Layout(
            title=self.plot_title,
            xaxis=dict(title='Tijd'),
            yaxis=dict(title='Waarnemingen [per week]'),
            margin=Margin(t=20),
        )