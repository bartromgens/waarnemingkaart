from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from observation.views import ObservationsView
from observation.views import SpeciesAutocomplete


urlpatterns = [
    url(r'^waarnemingen/$', ObservationsView.as_view(), name="observations"),
    url(r'^species-autocomplete/$', SpeciesAutocomplete.as_view(), name='species-autocomplete'),
]