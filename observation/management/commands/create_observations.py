import datetime
import dateparser
import time

from django.core.management.base import BaseCommand

from scraper import scraper

from observation.create import create_observations_for_date


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('date-start', nargs='+', type=str)
        parser.add_argument('date-end', nargs='+', type=str)
        parser.add_argument('--max', type=int, help='The max number of observations to create.', default=None)

    def handle(self, *args, **options):
        date_start_str = options['date-start'][0]
        date_end_str = options['date-end'][0]
        max_n = options['max']
        date_start = dateparser.parse(date_start_str).date()
        date_end = dateparser.parse(date_end_str).date()
        date = date_start
        print(date_start)
        print(date_end)
        while date <= date_end:
            for group_id in scraper.GROUP_IDS:
                observations = create_observations_for_date(group_id=group_id, date=date, max_n=max_n)
            date = date + datetime.timedelta(days=1)
