import logging

from django.db import models
from django.utils.text import slugify
from django.utils.functional import cached_property

from wikidata import wikidata

logger = logging.getLogger(__name__)


class BioClass(models.Model):
    name = models.CharField(max_length=1000, blank=True, default='')
    name_nl = models.CharField(max_length=1000, blank=True, default='')
    name_latin = models.CharField(max_length=1000, blank=True, default='')
    slug = models.SlugField(max_length=1000, blank=True, default='')
    wikidata_id = models.CharField(max_length=100, blank=True, default='')
    wikipedia_url_nl = models.URLField(max_length=1000, blank=True, null=True)
    wikimedia_image_url = models.URLField(max_length=1000, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name_nl)
        super().save(*args, **kwargs)

    @property
    def large_wikipedia_image_url(self):
        if not self.wikimedia_image_url:
            return ''
        return self.wikimedia_image_url.replace('400px', '1200px')

    class Meta:
        abstract = True


class Group(BioClass):
    def __str__(self):
        return self.name_nl

    @cached_property
    def n_observations(self):
        return Observation.objects.filter(group=self, coordinates__isnull=False).count()

    @cached_property
    def map_url(self):
        return "/kaart/?group={}".format(self.slug)


class Family(BioClass):
    group = models.ForeignKey(Group, null=True, blank=True)

    class Meta(BioClass.Meta):
        ordering = ['group__slug', 'name_nl']

    def __str__(self):
        return self.name_nl

    @cached_property
    def n_observations(self):
        return Observation.objects.filter(family=self, coordinates__isnull=False).count()

    @cached_property
    def n_species(self):
        return Species.objects.filter(family=self).count()

    @cached_property
    def map_url(self):
        return "/kaart/?group={}&family={}".format(self.group.slug, self.slug)


class Species(BioClass):
    family = models.ForeignKey(Family, null=True, blank=True)

    class Meta(BioClass.Meta):
        ordering = ['family__slug', 'name_nl']

    def __str__(self):
        return self.name_nl

    @cached_property
    def n_observations(self):
        return Observation.objects.filter(species=self, coordinates__isnull=False).count()

    @cached_property
    def map_url(self):
        return "/kaart/?group={}&family={}&species={}".format(self.family.group.slug, self.family.slug, self.slug)

    def add_wikidata(self):
        search_str = self.name_nl.lower()
        wikidata_id = wikidata.search_wikidata_id(search_str, language='nl')
        if not wikidata_id:
            logger.info('no wikidata entry found')
            return
        item = wikidata.WikidataItem(wikidata_id)
        self.wikidata_id = wikidata_id
        wikipedia_url_nl = item.get_wikipedia_url()
        if wikipedia_url_nl:
            self.wikipedia_url_nl = wikipedia_url_nl
        image_filename = item.get_image_filename()
        if image_filename:
            self.wikimedia_image_url = item.get_wikimedia_image_url(image_filename, image_width_px=400)
        self.save()


class Coordinates(models.Model):
    lat = models.FloatField(default=0.0)
    lon = models.FloatField(default=0.0)

    def __str__(self):
        return str(self.lat) + ', ' + str(self.lon)


class Observer(models.Model):
    name = models.CharField(max_length=2000, blank=True, default='')
    waarneming_user_url = models.URLField(max_length=1000, null=False, blank=True, default='', db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        self.id = self.id_from_waarneming_user_url
        super().save(*args, **kwargs)

    @property
    def id_from_waarneming_user_url(self):
        if self.waarneming_user_url:
            new_id = self.waarneming_user_url.split('/')[-1]
            return int(new_id)
        else:
            return self.id

    @cached_property
    def n_observations(self):
        return Observation.objects.filter(observer=self, coordinates__isnull=False).count()


class Observation(models.Model):
    species = models.ForeignKey(Species, null=True, blank=True)
    family = models.ForeignKey(Family, null=True, blank=True)
    group = models.ForeignKey(Group, null=True, blank=True)
    number = models.IntegerField(default=0)
    datetime = models.DateTimeField(null=True, blank=True, db_index=True)
    coordinates = models.ForeignKey(Coordinates, null=True, blank=True)
    waarneming_url = models.URLField(max_length=1000, null=True, blank=True, unique=True, db_index=True)
    observer = models.ForeignKey(Observer, null=True, blank=True)
    datetime_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-datetime', 'group__slug']

    def save(self, *args, **kwargs):
        self.id = self.id_from_waarneming_url
        super().save(*args, **kwargs)

    @property
    def id_from_waarneming_url(self):
        if self.waarneming_url:
            new_id = self.waarneming_url.split('/')[-1]
            return int(new_id)
        else:
            return self.id

    @staticmethod
    def all_complete():
        return Observation.objects.filter(datetime__isnull=False, coordinates__isnull=False)

    @staticmethod
    def all_need_update():
        return Observation.objects.all().exclude(datetime__isnull=False, coordinates__isnull=False, observer__isnull=False)


class BioClassObservationStats(models.Model):
    group = models.ForeignKey(Group, null=True, blank=True)
    family = models.ForeignKey(Family, null=True, blank=True)
    species = models.ForeignKey(Species, null=True, blank=True)
    n_observations = models.IntegerField(default=0)

    @staticmethod
    def observation_count_group(group):
        return BioClassObservationStats.objects.get(group=group).n_observations

    @staticmethod
    def observation_count_family(family):
        return BioClassObservationStats.objects.get(family=family).n_observations

    @staticmethod
    def observation_count_species(species):
        return BioClassObservationStats.objects.get(species=species).n_observations
