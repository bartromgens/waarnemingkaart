from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from observation.views import ObservationsView
from observation.views import SpeciesAutocomplete
from observation.views import FamilyAutocomplete
from observation.views import GroupAutocomplete
from observation.views import get_family_species_panel_html


urlpatterns = [
    url(r'^waarnemingen/$', ObservationsView.as_view(), name="observations"),
    url(r'^species-autocomplete/$', SpeciesAutocomplete.as_view(), name='species-autocomplete'),
    url(r'^family-autocomplete/$', FamilyAutocomplete.as_view(), name='family-autocomplete'),
    url(r'^group-autocomplete/$', GroupAutocomplete.as_view(), name='group-autocomplete'),
    url(r'^bioclass/family/species/$', get_family_species_panel_html, name='family-species-panel-html'),
]
