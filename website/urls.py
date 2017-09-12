from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from website.views import ContactView
from website.views import UserProfileView

from observation.views import ObservationMapView

import observation.urls

import website.api


urlpatterns = [
    url(r'^$', ObservationMapView.as_view(), name='homepage'),
    url(r'^about/$', TemplateView.as_view(template_name="website/about.html"), name='about'),
    url(r'^contact/$', ContactView.as_view(), name='contact'),
    url(r'^contribute/$', TemplateView.as_view(template_name="website/contribute.html"), name='contribute'),

    url(r'^userprofile/(?P<pk>[0-9]+)/$', login_required(UserProfileView.as_view()), name='userprofile'),

    url(r'^accounts/', include('registration.backends.simple.urls')),  # the django-registration module

    url(r'', include(observation.urls.urlpatterns)),

    url(r'^admin/', admin.site.urls),

    url(r'^api/', include(website.api)),

]


# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns += [
#         url(r'^__debug__/', include(debug_toolbar.urls)),
#     ]
