import datetime
import dateparser
import time

from django.core.management.base import BaseCommand
from django.db import transaction

from scraper import scraper

from observation.models import Observation
from observation.models import Observer
from observation.models import Coordinates
from observation.models import Group
from observation.models import Family
from observation.models import Species

from observation.create import ObservationFactory


class Command(BaseCommand):

    def handle(self, *args, **options):
        observations = Observation.all_need_update()
        n_observations = observations.count()
        print(str(n_observations) + ' to update')
        counter = 0
        for observation in observations:
            observation = ObservationFactory(observation.waarneming_url).create()
            if observation and observation.datetime:
                print(str(counter) + ' ' + str(observation.datetime))
            counter += 1
        print('END updating observations')
