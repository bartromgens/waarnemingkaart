import dateparser

from django.core.management.base import BaseCommand

from observation.models import Observation
from observation.models import Group
from observation.models import Species
from observation.models import Family
from observation.models import BioClassObservationStats


class Command(BaseCommand):

    def handle(self, *args, **options):
        objs = Group.objects.all()
        for ob in objs:
            stats, created = BioClassObservationStats.objects.get_or_create(
                group=ob
            )
            observations = Observation.objects.filter(group=ob, coordinates__isnull=False)
            stats.n_observations = observations.count()
            stats.save()

        objs = Family.objects.all()
        for ob in objs:
            stats, created = BioClassObservationStats.objects.get_or_create(
                family=ob
            )
            observations = Observation.objects.filter(family=ob, coordinates__isnull=False)
            stats.n_observations = observations.count()
            stats.save()

        objs = Species.objects.all()
        for ob in objs:
            stats, created = BioClassObservationStats.objects.get_or_create(
                species=ob
            )
            observations = Observation.objects.filter(species=ob, coordinates__isnull=False)
            stats.n_observations = observations.count()
            stats.save()
