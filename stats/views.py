from django.views.generic import TemplateView
from django.http import HttpResponse
from django.utils.safestring import mark_safe

from observation.models import Observation

from stats.plots import PlotObservationsVsTime


class ObservationsVsTimeView(TemplateView):
    template_name = "stats/observations_vs_time.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        observation_datetimes = list(Observation.all_complete().values_list('datetime', flat=True))
        context['plot_html'] = mark_safe(PlotObservationsVsTime(observation_datetimes).create_plot())
        context['n_observations'] = len(observation_datetimes)
        return context
