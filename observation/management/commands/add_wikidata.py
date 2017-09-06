import datetime
import dateparser

from django.core.management.base import BaseCommand

from scraper import scraper

from wikidata import wikidata

from observation.models import Observation
from observation.models import Coordinates
from observation.models import Group
from observation.models import Family
from observation.models import Species


class Command(BaseCommand):
    # def add_arguments(self, parser):
    #     parser.add_argument('date', nargs='+', type=str)
    #     parser.add_argument('--max', type=int, help='The max number of observations to create.', default=None)

    def handle(self, *args, **options):
        species = Species.objects.all()
        for spe in species:
            print(spe)
            search_str = spe.name_nl.lower()
            language = 'nl'
            id = wikidata.search_wikidata_id(search_str, language)
            if not id:
                print('no wikidata entry found')
                continue
            print(id)
            item = wikidata.WikidataItem(id)
            print(item.get_label())
            spe.wikimedia_id = id
            wikipedia_url_nl = item.get_wikipedia_url()
            if wikipedia_url_nl:
                print(wikipedia_url_nl)
                spe.wikipedia_url_nl = wikipedia_url_nl
            image_filename = item.get_image_filename()
            if image_filename:
                spe.wikimedia_image_url = item.get_wikimedia_image_url(image_filename)
            spe.save()
