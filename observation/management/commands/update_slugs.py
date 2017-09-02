import dateparser

from django.core.management.base import BaseCommand

from observation.models import Observation
from observation.models import Group
from observation.models import Species
from observation.models import Family


class Command(BaseCommand):

    def handle(self, *args, **options):
        objs = Group.objects.all()
        for ob in objs:
            ob.save()
        objs = Species.objects.all()
        for ob in objs:
            ob.save()
        objs = Family.objects.all()
        for ob in objs:
            ob.save()

