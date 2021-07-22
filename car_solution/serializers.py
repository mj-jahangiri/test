from rest_framework import serializers
from car_solution.models import Person, Car, Nod, Road, Stations


class PersonCarTollSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    national_code = serializers.CharField()
    age = serializers.IntegerField()
    total_toll_paid = serializers.IntegerField()
    car_toll_over_period = serializers.IntegerField()


class PersonModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'


class CarModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'


class AllNodeModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nod
        fields = '__all__'


class StationsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stations
        fields = '__all__'


class RoadModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Road
        fields = '__all__'
