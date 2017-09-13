from observation.models import Observation
from observation.models import Coordinates
from observation.models import Group
from observation.models import Family
from observation.models import Species

from rest_framework import serializers, viewsets


class BioClassSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'name_nl', 'name_latin', 'url', 'wikidata_id', 'wikipedia_url_nl', 'wikimedia_image_url')


class GroupSerializer(BioClassSerializer):
    class Meta(BioClassSerializer.Meta):
        model = Group


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class FamilySerializer(BioClassSerializer):
    class Meta(BioClassSerializer.Meta):
        model = Family


class FamilyViewSet(viewsets.ModelViewSet):
    queryset = Family.objects.all()
    serializer_class = FamilySerializer


class SpeciesSerializer(BioClassSerializer):
    class Meta(BioClassSerializer.Meta):
        model = Species


class SpeciesViewSet(viewsets.ModelViewSet):
    queryset = Species.objects.all()
    serializer_class = SpeciesSerializer


class CoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinates
        fields = ('lat', 'lon')


class CoordinatesViewSet(viewsets.ModelViewSet):
    queryset = Coordinates.objects.all()
    serializer_class = CoordinatesSerializer


class ObservationSerializer(serializers.HyperlinkedModelSerializer):
    species = SpeciesSerializer(read_only=True)
    family = FamilySerializer(read_only=True)
    group = GroupSerializer(read_only=True)
    coordinates = CoordinatesSerializer(read_only=True)

    class Meta:
        model = Observation
        fields = ('id', 'url', 'species', 'family', 'group', 'datetime', 'number', 'coordinates', 'waarneming_url')


class ObservationViewSet(viewsets.ModelViewSet):
    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer
