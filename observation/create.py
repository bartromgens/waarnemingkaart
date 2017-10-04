import time
import logging

from django.db import transaction

from observation.models import Observation
from observation.models import Observer
from observation.models import Coordinates
from observation.models import Group
from observation.models import Family
from observation.models import Species

# from scraper.scraper import ObservationScraper
# from scraper.scraper import get_observation_urls_for_date

logger = logging.getLogger(__name__)


def create_observations_for_date(group_id, date, max_n=None):
    logger.info('BEGIN: ' + str(date))
    observations = []
    observation_urls = get_observation_urls_for_date(group_id=group_id, date=date, max_n=max_n)
    for url in observation_urls:
        existing_observations = Observation.objects.filter(waarneming_url=url)
        if existing_observations.exists():
            logger.warning('WARNING: observation already exists, skipping!')
            continue
        observation = ObservationFactory(url).create()
        observations.append(observation)
    logger.info('END: ' + str(date))
    return observations


class ObservationFactory(object):
    required_keys = ['url', 'name_latin', 'name', 'family_latin', 'family', 'group',
                     'observer_name', 'observer_url', 'number']

    def __init__(self, observation_url):
        super().__init__()
        self.url = observation_url
        self.data = ObservationScraper(observation_url).create()

    @transaction.atomic
    def create(self):
        logger.info('BEGIN')
        start = time.time()
        self.correct_data(self.data)
        correct = self.check_data(self.data)
        if not correct:
            logger.warning(self.data)
            logger.warning('input data not correct, observation model will not be created')
            return None

        Observation.objects.filter(waarneming_url=self.url).delete()

        coordinates = ObservationFactory.get_or_create_coordinates(self.data)
        group = ObservationFactory.get_or_create_group(self.data)
        family = ObservationFactory.get_or_create_family(self.data, group)
        species = ObservationFactory.get_or_create_species(self.data, family)
        observer = ObservationFactory.get_or_create_observer(self.data)
        observation_new = Observation.objects.create(
            species=species,
            family=family,
            group=group,
            number=self.data['number'],
            datetime=self.data['datetime'],
            coordinates=coordinates,
            waarneming_url=self.url,
            observer=observer
        )
        logger.info('END - time: ' + str(time.time() - start))
        return observation_new

    @staticmethod
    def check_data(data):
        if not ObservationFactory.check_keys_and_value_exist(data, ObservationFactory.required_keys):
            return False
        return True

    @staticmethod
    def check_keys_and_value_exist(data, required_keys):
        for key in required_keys:
            if key not in data or not data[key]:
                return False
        return True

    @staticmethod
    def correct_data(data):
        if not data['name_latin'] and data['name']:
            data['name_latin'] = data['name']
        if not data['name'] and data['name_latin']:
            data['name'] = data['name_latin']
        if not data['family_latin'] and data['family']:
            data['family_latin'] = data['family']
        if not data['family'] and data['family_latin']:
            data['family'] = data['family_latin']

    @staticmethod
    def species_name_latin(data):
        return ObservationFactory.get_first_or_second_choice(data, 'name_latin', 'name')

    @staticmethod
    def species_name_nl(data):
        return ObservationFactory.get_first_or_second_choice(data, 'name', 'name_latin')

    @staticmethod
    def family_name_nl(data):
        return ObservationFactory.get_first_or_second_choice(data, 'family', 'family_latin')

    @staticmethod
    def family_name_latin(data):
        return ObservationFactory.get_first_or_second_choice(data, 'family_latin', 'family')

    @staticmethod
    def get_first_or_second_choice(data, first_key, second_key):
        if data[first_key]:
            return data[first_key]
        elif data[second_key]:
            return data[second_key]
        return ''

    @staticmethod
    def get_or_create_group(data):
        group, created = Group.objects.get_or_create(name_nl=data['group'])
        return group

    @staticmethod
    def get_or_create_family(data, group):
        family, created = Family.objects.get_or_create(
            group=group,
            name_nl=ObservationFactory.family_name_nl(data),
            name_latin=ObservationFactory.family_name_latin(data),
        )
        return family

    @staticmethod
    def get_or_create_species(data, family):
        species, created = Species.objects.get_or_create(
            family=family,
            name_nl=ObservationFactory.species_name_nl(data),
            name_latin=ObservationFactory.species_name_latin(data),
        )
        if created:
            species.add_wikidata()
        return species

    @staticmethod
    def get_or_create_observer(data):
        observer, created = Observer.objects.get_or_create(
            name=data['observer_name'],
            waarneming_user_url=data['observer_url']
        )
        return observer

    @staticmethod
    def get_or_create_coordinates(data):
        if not data['coordinates']:
            return None
        coordinates, created = Coordinates.objects.get_or_create(
            lat=data['coordinates']['lat'],
            lon=data['coordinates']['lon']
        )
        return coordinates
