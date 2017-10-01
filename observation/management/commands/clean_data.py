from django.core.management.base import BaseCommand

from observation.models import Observation
from observation.models import Group
from observation.models import Family
from observation.models import Species


class Command(BaseCommand):
    def handle(self, *args, **options):
        Command.remove_bioclasses_no_observations()

    @staticmethod
    def remove_bioclasses_no_observations():
        groups = Group.objects.all()
        families = Family.objects.all()
        species = Species.objects.all()
        Command.delete_bioclasses_without_observations(groups)
        Command.delete_bioclasses_without_observations(families)
        Command.delete_bioclasses_without_observations(species)
        Command.delete_unknown_bioclasses()

    @staticmethod
    def delete_bioclasses_without_observations(bioclasses):
        for bioclass in bioclasses:
            if bioclass.n_observations == 0:
                bioclass.delete()

    @staticmethod
    def delete_unknown_bioclasses():
        groups = Group.objects.filter(name_nl='onbekend').delete()
        families = Family.objects.filter(name_nl='onbekend').delete()
        species = Species.objects.filter(name_nl='onbekend').delete()
