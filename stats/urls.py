from django.conf.urls import url

from stats.views import ObservationsVsTimeView


urlpatterns = [
    url(r'^stats/waarnemingen/$', ObservationsVsTimeView.as_view(), name="observations_vs_time"),
]