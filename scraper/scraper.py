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
    observation_urls = get_observation_urls(group_id, date, max_n)
    if max_n:
        return observation_urls[:max_n]
    return observation_urls


def get_observation_urls(group_id, date, max_n=None):
    page_url = WAARNEMINGEN_URL + '/fieldwork/observations'
    observation_urls = set()
    success = True
    page = 1
    while success:
        logger.info('get page: {}'.format(page))
        args = {
            'species_group': str(group_id),
            'after_date': date.isoformat(),
            'before_date': date.isoformat(),
            'page': str(page),
        }
        response = requests.get(page_url, args)
        success = response.status_code == 200
        if not success:
            break
        page += 1
        tree = lxml.html.fromstring(response.content)
        table_columns = tree.xpath('//table[@class="table table-bordered table-striped"]/tbody/tr/td/a')
        for row in table_columns:
            observation_url = WAARNEMINGEN_URL + row.get('href')
            if '/observation/' in observation_url:
                observation_urls.add(observation_url)
        if max_n and len(observation_urls) >= max_n:
            break
    logger.info(str(len(observation_urls)) + ' species found on ' + date.isoformat() + ' for url: ' + str(response.url))
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
        logger.info('html: {}'.format(self.html))
        self.parse()
        logger.info('data: {}'.format(self.data))
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
        refs = self.html.xpath('//span [@class="teramap-coordinates-coords"]')
        for ref in refs:
            match = re.search("[0-9.]+, [0-9.]+", ref.text.strip())
            if match:
                gps_coordinates_str = match.group().split(',')
                coordinates = {
                    'lat': float(gps_coordinates_str[0]),
                    'lon': float(gps_coordinates_str[1]),
                }
                return coordinates
        return {}

    def parse_name(self):
        common_names = self.html.xpath('//h1/a/span[@class="species-common-name"]')
        name = ''
        if common_names:
            name = common_names[0].text.strip()
            name = name.replace('-', '').strip()
        latin_names = self.html.xpath('//h1/small/i[@class="species-scientific-name"]')
        name_latin = ''
        if latin_names:
            name_latin = latin_names[0].text.strip()
        return name, name_latin

    def parse_family(self):
        main_info_links = self.html.xpath('//div[@class="app-content-subtitle"]/div/a')
        for link in main_info_links:
            if 'taxa' in link.get('href'):
                family_full = link.text.strip()
                match = re.search(r"(.+)\s\((.+)\)", family_full)
                if match is None:
                    logger.warning('latin name not found in: ' + family_full)
                    return family_full, family_full
                family = match.groups()[0]
                family_latin = match.groups()[1]
                return family, family_latin
        return '', ''

    def parse_group(self):
        main_info_spans = self.html.xpath('//div[@class="app-content-subtitle"]/div/span[@class="label label-success"]')
        for span in main_info_spans:
            return span.text.strip()
        return ''

    def parse_info_table(self):
        table_rows = self.html.xpath('//table[@class="table table-condensed"]/tr')
        timezone_amsterdam = pytz.timezone('Europe/Amsterdam')
        datetime_observation = None
        observer_name = ''
        observer_url = ''
        number = 0
        for row in table_rows:
            ths = row.xpath('th')
            tds = row.xpath('td')
            if not ths or not tds:
                logger.warning('could not find info table on page: {}'.format(self.url))
                continue
            th = ths[0]
            td = tds[0]
            th_text = th.text.strip() if th.text else ''
            td_text = td.text.strip() if td.text else ''
            if 'datum' in th_text:
                datetime_str = td_text
                datetime_obj = dateparser.parse(datetime_str)
                if datetime_obj is None:
                    logger.warning('datetime not found')
                ams_dt = timezone_amsterdam.localize(datetime_obj)
                datetime_utc_tzaware = ams_dt.astimezone(pytz.utc)
                datetime_observation = datetime_utc_tzaware
            if 'aantal' in th_text:
                number_str = td_text
                match = re.search(r"(\d+)", number_str)
                number = int(match.groups()[0].strip())
            if 'waarnemer' in th_text:
                links = td.xpath('a')
                if links:
                    observer_name = td.xpath('a')[0].text.strip()
                    observer_url = 'https://waarneming.nl' + td.xpath('a')[0].get('href')
        return datetime_observation, number, observer_name, observer_url

    @property
    def data(self):
        return {
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
