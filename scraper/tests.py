import datetime
import json
import pprint

from django.test import TestCase

from scraper import scraper

pp = pprint.PrettyPrinter(indent=4)


class TestObservationListScraper(TestCase):

    def test_scrape_observations(self):
        date = datetime.date(year=2017, month=9, day=1)
        max_n = 2
        observation_urls = scraper.get_observation_urls(scraper.VOGELS_ID, date, max_n=max_n)
        print(observation_urls)


class TestObservationScraper(TestCase):

    def test_scrape_observation_data(self):
        urls = [
            'https://waarneming.nl/observation/143525935',
            'https://waarneming.nl/observation/143525930',
            'https://waarneming.nl/observation/143528701',
            'https://waarneming.nl/observation/143878912',
        ]
        for url in urls:
            observation = scraper.ObservationScraper(url)
            observation.create()
            print(observation)
