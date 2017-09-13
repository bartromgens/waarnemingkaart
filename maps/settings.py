from django.conf import settings

MAPS_DATA_DIR = getattr(settings, 'MAPS_DATA_DIR', '')
