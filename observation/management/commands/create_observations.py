import datetime
import dateparser
import time

from django.core.management.base import BaseCommand

from scraper import scraper

from observation.create import create_observations_for_date


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('date', nargs='+', type=str)
        parser.add_argument('--max', type=int, help='The max number of observations to create.', default=None)

    def handle(self, *args, **options):
        date_str = options['date'][0]
        max_n = options['max']
        date = dateparser.parse(date_str).date()
        end_date = datetime.date(year=2015, month=1, day=1)
        while date >= end_date:
            for group_id in scraper.GROUP_IDS:
                observations = create_observations_for_date(group_id=group_id, date=date, max_n=max_n)
            date = date - datetime.timedelta(days=1)
