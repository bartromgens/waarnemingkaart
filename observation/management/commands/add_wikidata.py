from django.core.management.base import BaseCommand

from observation.models import Species


class Command(BaseCommand):
    # def add_arguments(self, parser):
    #     parser.add_argument('date', nargs='+', type=str)
    #     parser.add_argument('--max', type=int, help='The max number of observations to create.', default=None)

    def handle(self, *args, **options):
        species = Species.objects.all()
        for spe in species:
            spe.add_wikidata()
