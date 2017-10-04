from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from website.views import AboutView
from website.views import UserProfileView
from website.views import HomeView

from observation.views import ObservationMapView

import observation.urls
import stats.urls

import website.api


urlpatterns = [
    url(r'^$', HomeView.as_view(), name='homepage'),
    url(r'^kaart/$', ObservationMapView.as_view(), name='observation-map'),
    url(r'^info/$', AboutView.as_view(), name='about'),
    url(r'^api/$', TemplateView.as_view(template_name="website/api.html"), name='api-info'),

    url(r'^userprofile/(?P<pk>[0-9]+)/$', login_required(UserProfileView.as_view()), name='userprofile'),

    url(r'^accounts/', include('registration.backends.simple.urls')),  # the django-registration module

    url(r'', include(observation.urls.urlpatterns)),
    url(r'', include(stats.urls.urlpatterns)),

    url(r'^admin/', admin.site.urls),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
