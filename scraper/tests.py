import datetime
import json
import pprint

from django.test import TestCase

from scraper import scraper

pp = pprint.PrettyPrinter(indent=4)


class TestObservationListScraper(TestCase):

    def test_scrape_observations(self):
        date = datetime.date(year=2017, month=9, day=1)
        observation_list_urls = scraper.get_observation_list_urls(scraper.VOGELS_ID, date)
        observation_urls_species = scraper.get_observation_urls_from_list_page(observation_list_urls[0])
        print(observation_urls_species)
        observation_urls_species = scraper.get_observation_urls_from_list_page(observation_list_urls[20])
        print(observation_urls_species)
        observation_urls_species = scraper.get_observation_urls_from_list_page(observation_list_urls[40])
        print(observation_urls_species)


class TestObservationScraper(TestCase):

    def test_scrape_observation_data(self):
        urls = [
            'https://waarneming.nl/waarneming/view/143525935',
            'https://waarneming.nl/waarneming/view/143525930',
            'https://waarneming.nl/waarneming/view/143528701',
        ]
        for url in urls:
            observation = scraper.Observation(url)
            observation.create()
            print(observation)
