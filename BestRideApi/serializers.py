from django.core.serializers import serialize
from rest_framework import serializers
from sqlparse.tokens import Assignment

from .models import *
from rest_framework_gis.serializers import GeoFeatureModelSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['idUser', 'name', 'email', 'dob', 'phone_number', 'address', 'postal_code', 'gender']


class EmergencyContactDriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContactDriver
        fields = '__all__'


class DriverSerializer(serializers.ModelSerializer):
    emergency_contact_id = EmergencyContactDriverSerializer()

    class Meta:
        model = Driver
        fields = ['idDriver', 'email', 'name', 'dob', 'gender', 'address', 'postal_code', 'country',
                  'nif', 'rnat_license', 'driver_license', 'phone_number', 'nationality', 'citizen_card',
                  'ancat_number', 'iban', 'special_need_suppport', 'languages', 'vehicles_can_drive',
                  'available_hours', 'course_taken', 'emergency_contact_id', 'type_guide', 'about', 'video',
                  'start_activity']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['idCompany', 'name', 'rnat_license', 'email', 'phone', 'address', 'postal_code', 'country', 'nif',
                  'phone_number']


class FKDriverEnterpriseSerializer(serializers.ModelSerializer):
    driver = DriverSerializer(read_only=True)
    empresaDriver = CompanySerializer(read_only=True)

    class Meta:
        model = FKDriverEnterprise
        fields = '__all__'


class InterestPointsSerializer(serializers.ModelSerializer):
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
