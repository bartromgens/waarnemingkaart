from django.db import models
from django.utils.text import slugify


class BioClass(models.Model):
    name = models.CharField(max_length=1000, blank=True, default='')
    name_nl = models.CharField(max_length=1000, blank=True, default='')
    name_latin = models.CharField(max_length=1000, blank=True, default='')
    slug = models.SlugField(max_length=1000, blank=True, default='')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name_nl)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name_nl']
        abstract = True


class Group(BioClass):
    def __str__(self):
        return self.name_nl


class Species(BioClass):
    def __str__(self):
        return self.name_nl + ' (' + self.name_latin + ')'


class Family(BioClass):
    def __str__(self):
        return self.name_nl + ' (' + self.name_latin + ')'


class Coordinates(models.Model):
    lat = models.FloatField(default=0.0)
    lon = models.FloatField(default=0.0)

    def __str__(self):
        return str(self.lat) + ', ' + str(self.lon)


class Observation(models.Model):
    species = models.ForeignKey(Species, null=True, blank=True)
    family = models.ForeignKey(Family, null=True, blank=True)
    group = models.ForeignKey(Group, null=True, blank=True)
    number = models.IntegerField(default=0)
    datetime = models.DateTimeField(null=True, blank=True, db_index=True)
    coordinates = models.ForeignKey(Coordinates, null=True, blank=True)
    waarneming_url = models.URLField(null=True, blank=True, unique=True, db_index=True)

    class Meta:
        ordering = ['species']

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
