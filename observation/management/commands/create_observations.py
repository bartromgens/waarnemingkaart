import dateparser

from django.core.management.base import BaseCommand

from scraper import scraper

from observation.models import Observation
from observation.models import Coordinates
from observation.models import Group
from observation.models import Family
from observation.models import Species


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('date', nargs='+', type=str)
        parser.add_argument('--max', type=int, help='The max number of observations to create.', default=None)

    def handle(self, *args, **options):
        date_str = options['date'][0]
        max_n = options['max']
        date = dateparser.parse(date_str).date()
        observations = scraper.get_observations_for_date(species_id=scraper.VOGELS_ID, date=date, max_n=max_n)
        for observation in observations:
            existing_observations = Observation.objects.filter(waarneming_url=observation.url)
            if existing_observations:
                print('WARNING: observation already exists, skipping to next')
                continue
            observation.create()
            print(observation)
            data = observation.data
            species, created = Species.objects.get_or_create(
                name_nl=data['name'],
                name_latin=data['name_latin'],
            )
            family, created = Family.objects.get_or_create(
                name_nl=data['family'],
                name_latin=data['family_latin'],
            )
            group, created = Group.objects.get_or_create(
                name_nl=data['group'],
            )
            if not data['coordinates']:
                coordinates = None
            else:
                coordinates, created = Coordinates.objects.get_or_create(
                    lat=data['coordinates']['lat'],
                    lon=data['coordinates']['lon'],
                )

            Observation.objects.filter(waarneming_url=data['url']).delete()
            observation_new = Observation.objects.create(
                species=species,
                family=family,
                group=group,
                number=data['number'],
                datetime=data['datetime'],
                coordinates=coordinates,
                waarneming_url=data['url'],
            )
            # observation_new.id =
            # observation_new.save()
