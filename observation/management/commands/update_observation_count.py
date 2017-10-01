from django.core.management.base import BaseCommand

from observation.models import update_observation_counts


class Command(BaseCommand):
    def handle(self, *args, **options):
        update_observation_counts()
