import os

from django.core.management.base import BaseCommand
from django.conf import settings

from website.backup import create_json_dump


class Command(BaseCommand):

    def handle(self, *args, **options):
        filepath = os.path.join(settings.MAPS_DATA_DIR, 'observations.json')
        create_json_dump(filepath)
