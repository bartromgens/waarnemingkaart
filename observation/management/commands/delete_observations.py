from django.core.management.base import BaseCommand

from observation.models import Observation


class Command(BaseCommand):
    def handle(self, *args, **options):
        Observation.objects.all().delete()
