import dateparser

from django.core.management.base import BaseCommand

from scraper import scraper


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('date', nargs='+', type=str)

    def handle(self, *args, **options):
        date_str = options['date'][0]
        date = dateparser.parse(date_str).date()
        observations = scraper.get_observations_for_date(species_id=scraper.VOGELS_ID, date=date, max_n=1000)
        for observation in observations:
            observation.create()
            print(observation)
