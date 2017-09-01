from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=1000, blank=True, default='')
    name_nl = models.CharField(max_length=1000, blank=True, default='')
    name_latin = models.CharField(max_length=1000, blank=True, default='')

    def __str__(self):
        return self.name_nl


class Species(models.Model):
    name = models.CharField(max_length=1000, blank=True, default='')
    name_nl = models.CharField(max_length=1000, blank=True, default='')
    name_latin = models.CharField(max_length=1000, blank=True, default='')

    def __str__(self):
        return self.name_nl + ' (' + self.name_latin + ')'


class Family(models.Model):
    name = models.CharField(max_length=1000, blank=True, default='')
    name_nl = models.CharField(max_length=1000, blank=True, default='')
    name_latin = models.CharField(max_length=1000, blank=True, default='')

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
    datetime = models.DateTimeField(null=True, blank=True)
    coordinates = models.ForeignKey(Coordinates, null=True, blank=True)
    url = models.URLField(null=True, blank=True, unique=True)
