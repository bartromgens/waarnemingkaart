from observation.models import Observation
from observation.models import Coordinates
from observation.models import Group
from observation.models import Family
from observation.models import Species

from rest_framework import serializers, viewsets


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name', 'name_nl', 'name_latin')


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = ('name', 'name_nl', 'name_latin')


class FamilyViewSet(viewsets.ModelViewSet):
    queryset = Family.objects.all()
    serializer_class = FamilySerializer


class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        fields = ('name', 'name_nl', 'name_latin')


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
    id = serializers.HyperlinkedRelatedField(view_name='observation-detail', read_only=True)
    species = SpeciesSerializer(read_only=True)
    family = FamilySerializer(read_only=True)
    group = GroupSerializer(read_only=True)
    coordinates = CoordinatesSerializer(read_only=True)

    class Meta:
        model = Observation
        fields = ('id', 'url', 'species', 'family', 'group', 'datetime', 'number', 'coordinates')


class ObservationViewSet(viewsets.ModelViewSet):
    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer
