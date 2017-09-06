import logging
import urllib.parse

import requests

logger = logging.getLogger(__name__)


def search(search_str, language='en'):
    search_url = 'https://www.wikidata.org/w/api.php'
    params = {
        'action': 'wbsearchentities',
        'format': 'json',
        'search': search_str,
        'language': language,
    }
    response = requests.get(search_url, params, timeout=60)
    return response.json()


def search_wikidata_id(search_str, language='en'):
    ids = search_wikidata_ids(search_str, language)
    if ids:
        return ids[0]
    return ''


def search_wikidata_ids(search_str, language='en'):
    results = search(search_str, language)
    ids = []
    if 'search' in results:
        for result in results['search']:
            ids.append(result['id'])
    return ids


class WikidataItem(object):

    def __init__(self, wikidata_id, language='nl'):
        self.id = wikidata_id
        site = 'wiki' + language
        self.item = self.get_item(wikidata_id, sites=site)

    @staticmethod
    def get_item(id, sites=None, props=None):
        assert id
        url = 'https://www.wikidata.org/w/api.php'
        params = {
            'action': 'wbgetentities',
            'ids': id,
            'format': 'json'
        }
        if sites:
            params['sites'] = sites
        if props:
            params['props'] = props
        response = requests.get(url, params, timeout=60)
        reponse_json = response.json()
        item = reponse_json['entities'][id]
        return item

    def get_claims(self):
        return self.item['claims']

    def get_parts(self):
        claims = self.get_claims()
        if 'P527' in claims:
            return claims['P527']  # has part
        return None

    def get_given_names(self):
        claims = self.get_claims()
        if 'P735' in claims:
            given_names = []
            for value in claims['P735']:
                given_names.append(WikidataItem.get_label_for_id(value['mainsnak']['datavalue']['value']['id']))
            return given_names
        return ''

    def get_image_filename(self):
        claims = self.get_claims()
        if 'P18' in claims:
            return claims['P18'][0]['mainsnak']['datavalue']['value']
        return ''

    @staticmethod
    def get_label_for_id(id, language='nl'):
        item = WikidataItem.get_item(id, props='labels')
        return WikidataItem.get_label_from_item(item, language=language)

    def get_label(self, language='nl'):
        return WikidataItem.get_label_from_item(self.item, language=language)

    def get_short_name(self, language='nl'):
        claims = self.get_claims()
        if 'P1813' in claims:
            for claim in claims['P1813']:
                if claim['mainsnak']['datavalue']['value']['language'] == language:
                    return claim['mainsnak']['datavalue']['value']['text']
        return ''

    @staticmethod
    def get_label_from_item(item, language='nl'):
        if 'labels' not in item or language not in item['labels']:
            return ''
        title = item['labels'][language]['value']
        return title

    def get_wikipedia_url(self, language='nl'):
        site = language + 'wiki'
        if 'sitelinks' not in self.item or site not in self.item['sitelinks']:
            logger.info('wikipedia url not found for wikidata item: ' + str(self.id))
            return ''
        title = self.item['sitelinks'][site]['title']
        url = 'https://' + language + '.wikipedia.org/wiki/' + urllib.parse.quote(title)
        return url

    @staticmethod
    def get_wikimedia_image_url(filename, image_width_px=220):
        url = 'https://commons.wikimedia.org/w/api.php'
        params = {
            'action': 'query',
            'titles': 'File:' + filename,
            'prop': 'imageinfo',
            'iiprop': 'url',
            'iiurlwidth': str(image_width_px),
            'format': 'json',
        }
        response = requests.get(url, params, timeout=60)
        response_json = response.json()
        pages = response_json['query']['pages']
        for page in pages.values():
            if 'imageinfo' in page:
                wikimedia_image_url = page['imageinfo'][0]['thumburl']
                return wikimedia_image_url
        return ''
