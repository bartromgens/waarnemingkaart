import logging
import requests
import time
import re
import pprint
import json

import pytz
import dateparser

import lxml.html

logger = logging.getLogger(__name__)

WAARNEMINGEN_URL = 'https://waarneming.nl'

VOGELS_ID = 1
ZOOGDIEREN_ID = 2
REPTIELEN_AMFIBIEEN_ID = 3
DAGVLINDERS_ID = 4
LIBELLEN_ID = 5
INSECTEN_OVERIG_ID = 6
WEEKDIEREN_ID = 7
NACHTVLINDERS_ID = 8
VISSEN_ID = 9
PLANTEN_ID = 10
PADDENSTOELEN_ID = 11
MOSSEN_ID = 12
GELEEDPOTIGEN_ID = 13
SPRINKHANEN_ID = 14
WANTSEN_CICADEN_LUIZEN_ID = 15
KEVERS_ID = 16
BIJEN_WESPEN_MIEREN_ID = 17
VLIEGEN_MUGGEN_ID = 18
ALGEN_WIEREN_EENCELLIGEN_ID = 19
ONGEWERVELDEN_ID = 20
VERSTORINGEN_ID = 30

GROUP_IDS = [
    VOGELS_ID,
    ZOOGDIEREN_ID,
    # REPTIELEN_AMFIBIEEN_ID,
    DAGVLINDERS_ID,
    # LIBELLEN_ID,
    # INSECTEN_OVERIG_ID,
    # WEEKDIEREN_ID,
    # NACHTVLINDERS_ID,
    # VISSEN_ID,
    # PLANTEN_ID,
    # PADDENSTOELEN_ID,
    # MOSSEN_ID,
    # GELEEDPOTIGEN_ID,
    # SPRINKHANEN_ID,
    # WANTSEN_CICADEN_LUIZEN_ID,
    # KEVERS_ID,
    # BIJEN_WESPEN_MIEREN_ID,
    # VLIEGEN_MUGGEN_ID,
    # ALGEN_WIEREN_EENCELLIGEN_ID,
    # ONGEWERVELDEN_ID,
    # VERSTORINGEN_ID,
]
# GROUP_IDS = [VOGELS_ID]

pp = pprint.PrettyPrinter(indent=4)


def get_observation_urls_for_date(group_id, date, max_n=None):
    observation_list_urls = get_observation_list_urls(group_id, date)
    observation_urls = []
    for list_url in observation_list_urls:
        observation_urls += get_observation_urls_from_list_page(list_url)
        if max_n and len(observation_urls) >= max_n:
            break
    if max_n:
        return observation_urls[:max_n]
    return observation_urls


def get_observation_list_urls(group_id, date):
    page_url = WAARNEMINGEN_URL + '/waarnemingen_v7.php'
    args = {
        'groep': str(group_id),
        'datum': date.isoformat()
    }
    response = requests.get(page_url, args)
    tree = lxml.html.fromstring(response.content)
    table_columns = tree.xpath('//table[@class="paginator list nolistify"]/tr/td/a')
    observation_list_urls = set()
    for row in table_columns:
        observed_species_url = WAARNEMINGEN_URL + row.get('href')
        if '/soort/view/' in observed_species_url:
            # print(observed_species_url)
            observation_list_urls.add(observed_species_url)
    logger.info(str(len(observation_list_urls)) + ' species found on ' + date.isoformat() + ' for url: ' + str(response.url))
    return list(observation_list_urls)


def get_observation_urls_from_list_page(url):
    start = time.time()
    response = requests.get(url)
    response_time = time.time() - start
    tree = lxml.html.fromstring(response.content)
    table_columns = tree.xpath('//table[@class="paginator list nolistify"]/tr/td/a')
    observation_urls = set()
    for row in table_columns:
        observation_url = WAARNEMINGEN_URL + row.get('href')
        if '/waarneming/view/' in observation_url:
            # print(observation_url)
            observation_urls.add(observation_url)
    logger.info('\t response time: ' + str(response_time) + ' - ' + str(len(observation_urls)) + ' observations found for url: ' + str(response.url))
    return list(observation_urls)


class ObservationScraper(object):

    def __init__(self, url):
        self.url = url
        self.html = None
        self.name = ''
        self.name_latin = ''
        self.family = ''
        self.family_latin = ''
        self.group = ''
        self.number = 0
        self.datetime = None
        self.coordinates = {}
        self.observer_name = ''
        self.observer_url = ''

    def __str__(self):
        return str(pp.pformat(self.data))

    def create(self):
        self.html = self.get_html()
        self.parse()
        return self.data

    def get_html(self):
        start = time.time()
        response = requests.get(self.url)
        logger.info('response time: ' + str(time.time() - start))
        return lxml.html.fromstring(response.content)

    def parse(self):
        if self.html is None:
            logger.error('html is empty, please call get_html() first')
            return
        logger.info('BEGIN: ' + self.url)
        self.name, self.name_latin = self.parse_name()
        self.family, self.family_latin = self.parse_family()
        self.group = self.parse_group()
        self.datetime, self.number, self.observer_name, self.observer_url = self.parse_info_table()
        self.coordinates = self.parse_coordinates()

    def parse_coordinates(self):
        refs = self.html.xpath('//@href')
        for ref in refs:
            if 'https://maps.google.com/maps' in ref:
                match = re.search("[0-9\.]+,[0-9\.]+", ref)
                if match:
                    gps_coordinates_str = match.group().split(',')
                    coordinates = {
                        'lat': float(gps_coordinates_str[0]),
                        'lon': float(gps_coordinates_str[1]),
                    }
                    return coordinates
        return {}

    def parse_name(self):
        header_links = self.html.xpath('//h1/a')
        for link in header_links:
            if 'soort/view/' in link.get('href'):
                name_latin = link.getchildren()[0].text.strip()
                if link.text:
                    name = link.text.replace('-', '').strip()
                else:
                    name = name_latin
                return name, name_latin
        return '', ''

    def parse_family(self):
        main_info_links = self.html.xpath('//div[@class="content"]/p/a')
        for link in main_info_links:
            if 'familie/view/' in link.get('href'):
                family_full = link.text.strip()
                match = re.search(r"(.+)\s\((.+)\)", family_full)
                if match is None:
                    logger.warning('WARNING: latin name not found in: ' + family_full)
                    return family_full, family_full
                family = match.groups()[0]
                family_latin = match.groups()[1]
                return family, family_latin
        return '', ''

    def parse_group(self):
        main_info_spans = self.html.xpath('//div[@class="content"]/p/span')
        for span in main_info_spans:
            if 'Soortgroep:' in span.text:
                species = span.tail.strip()
                return species
        return ''

    def parse_info_table(self):
        table_cells = self.html.xpath('//table[@class="form"]/tr/td')
        timezone_amsterdam = pytz.timezone('Europe/Amsterdam')
        datetime_observation = None
        observer_name = ''
        observer_url = ''
        number = 0
        for cell in table_cells:
            if not cell.text:
                continue
            if 'Datum' in cell.text:
                datetime_str = cell.getnext().text
                if 'Vervaagd' in datetime_str:
                    continue
                # datetime_obj = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")  # 2017-09-01 09:15
                datetime_obj = dateparser.parse(datetime_str)
                if datetime_obj is None:
                    logger.warning('WARNING: datetime not found')
                ams_dt = timezone_amsterdam.localize(datetime_obj)
                datetime_utc_tzaware = ams_dt.astimezone(pytz.utc)
                datetime_observation = datetime_utc_tzaware
            if 'Aantal' in cell.text:
                number_str = cell.getnext().text
                match = re.search(r"(\d+)", number_str)
                number = int(match.groups()[0].strip())
            if 'Waarnemer' in cell.text:
                links = cell.getnext().xpath('a')
                if len(links) > 1:
                    observer_name = cell.getnext().xpath('a')[1].text
                    observer_url = 'https://waarneming.nl' + cell.getnext().xpath('a')[1].get('href')
        return datetime_observation, number, observer_name, observer_url

    @property
    def data(self):
        data = {
            'url': self.url,
            'name': self.name,
            'name_latin': self.name_latin,
            'family': self.family,
            'family_latin': self.family_latin,
            'group': self.group,
            'number': self.number,
            'datetime': self.datetime,
            'coordinates': self.coordinates,
            'observer_name': self.observer_name,
            'observer_url': self.observer_url,
        }
        return data

    def to_json(self):
        return json.dump(self.data)
