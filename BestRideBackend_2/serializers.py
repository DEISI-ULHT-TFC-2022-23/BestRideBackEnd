from django.core.serializers import serialize
from rest_framework import serializers
from sqlparse.tokens import Assignment

from .models import *
from rest_framework_gis.serializers import GeoFeatureModelSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class EmergencyContactDriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContactDriver
        fields = '__all__'


class DriverSerializer(serializers.ModelSerializer):
    emergencyContactDrive = EmergencyContactDriverSerializer()

    class Meta:
        model = Driver
        fields = '__all__'


class EmpresaDriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmpresaDriver
        fields = '__all__'


class FKDriverEnterpriseSerializer(serializers.ModelSerializer):
    driver = DriverSerializer(read_only=True)
    empresaDriver = EmpresaDriverSerializer(read_only=True)

    class Meta:
        model = FKDriverEnterprise
        fields = '__all__'


class InterestPointsSerializaer(serializers.ModelSerializer):
    class Meta:
        model = PointInterest
        geo_field = "point"
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


class RoadMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoadMap
        geo_field = "point"
        fields = '__all__'

    ##def create(self, validated_data):
    ##    pointInterests_data = validated_data.pop('pointInterest')
    ##    roadMap = RoadMap.objects.create(**validated_data)
    ##    for pointInterest in pointInterests_data:
    ##        PointInterest.objects.create(roadMap=roadMap, **pointInterest)
    ##    return roadMap


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'


class RoadVehicleSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(many=False)

    class Meta:
        model = RoadVehicle
        fields = '__all__'


class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = '__all__'


class TravelScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelSchedule
        fields = '__all__'


class TravelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Travel
        fields = '__all__'
