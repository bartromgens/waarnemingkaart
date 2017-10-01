from django.test import TestCase

from observation.create import ObservationFactory


class TestCreateObservations(TestCase):

    def test_create_observations(self):
        urls = [
            'https://waarneming.nl/waarneming/view/143525935',
            'https://waarneming.nl/waarneming/view/143525930',
            'https://waarneming.nl/waarneming/view/143528701',
            'https://waarneming.nl/waarneming/view/143878912',
        ]
        for url in urls:
            observation = ObservationFactory(url).create()
            print(observation)
