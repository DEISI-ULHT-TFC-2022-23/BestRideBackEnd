import logging
from datetime import datetime, timedelta

from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from BestRideBackend_2.serializers import *
from django.contrib.gis.geos import Point
from environs import Env
from azure.storage.blob import BlobServiceClient
import math

env = Env()
env.read_env()
# Configurar a conexão com o Azure Blob Storage
blob_service_client = BlobServiceClient.from_connection_string('<YOUR_CONNECTION_STRING>')

class Routes(APIView):

    @api_view(['POST'])
    def getRoadMap(self):
        KM_MAX = self.data['kmMAX']
        Road = RoadMap.objects.all()
        # aqui
        s3_client = None

        distance_dict = {}

        for rd in Road:
            p1 = Point(self.data['lat'], self.data['lng'])
            p2 = Point(rd.location.coords[0], rd.location.coords[1])
            distance = p1.distance(p2)
            distance_in_km = math.trunc(distance * 100)
            distance_dict[str(rd.title)] = distance_in_km

        for name, km in distance_dict.items():
            if km > KM_MAX:
                Road = Road.exclude(title=name)

        try:
            # Crie uma instância do cliente BlobServiceClient
            blob_service_client = BlobServiceClient.from_connection_string('<CONNECTION_STRING>')
            container_name = 'bestridecontainer'  # Nome do container no Azure Blob Storage

            for e in Road:
                blob_client = blob_service_client.get_blob_client(container_name, e.image)
                sas_token = blob_client.generate_shared_access_signature(permission='r', expiry=datetime.utcnow() + timedelta(hours=1))
                url = blob_client.url + '?' + sas_token
                e.image = url

        except Exception as e:
            logging.error(e)

        Road_Serializer = RoadMapSerializer(Road, many=True)
        return Response(Road_Serializer.data)

    @api_view(['POST'])
    def distance(request):
        Road = RoadMap.objects.all()

        distance_dict = {}

        for rd in Road:
            p1 = Point(request.data['lat'], request.data['lng'])
            p2 = Point(rd.location.coords[0], rd.location.coords[1])
            distance = p1.distance(p2)
            distance_in_km = math.trunc(distance * 100)
            distance_dict[str(rd.title)] = distance_in_km

        return JsonResponse(distance_dict)

    @api_view(['GET'])
    def roadMapByCity(self, city):
        # aqui
        s3_client = None
        roadMap = RoadMap.objects.filter(city_id__name=city)

        try:
            # Crie uma instância do cliente BlobServiceClient
            blob_service_client = BlobServiceClient.from_connection_string('<CONNECTION_STRING>')
            container_name = 'bestridecontainer'  # Nome do container no Azure Blob Storage

            for e in roadMap:
                blob_client = blob_service_client.get_blob_client(container_name, e.image)
                sas_token = blob_client.generate_shared_access_signature(permission='r',
                                                                         expiry=datetime.utcnow() + timedelta(hours=1))
                url = blob_client.url + '?' + sas_token
                e.image = url

        except Exception as e:
            logging.error(e)

        Road_Serializer = RoadMapSerializer(roadMap, many=True)
        return Response(Road_Serializer.data)

    @api_view(['GET'])
    def roadMapByEnterprise(self, enterprise):
        roadMap = RoadMap.objects.all().filter(enterprise=enterprise)
        roadMapSerializer = RoadMapSerializer(roadMap, many=True)
        return Response(roadMapSerializer.data)

    @api_view(['GET'])
    def roadMapById(self, id):
        roadMap = RoadMap.objects.all().filter(id=id)
        roadMapSerializer = RoadMapSerializer(roadMap, many=True)
        return Response(roadMapSerializer.data)

    @api_view(['GET'])
    def getPointsInterest(self):
        # aqui
        s3_client = None
        Points = PointInterest.objects.all()

        try:
            # Crie uma instância do cliente BlobServiceClient
            blob_service_client = BlobServiceClient.from_connection_string('<CONNECTION_STRING>')
            container_name = 'bestridecontainer'  # Nome do container no Azure Blob Storage

            for point in Points:
                blob_client = blob_service_client.get_blob_client(container_name, point.image)
                sas_token = blob_client.generate_shared_access_signature(permission='r',
                                                                         expiry=datetime.utcnow() + timedelta(hours=1))
                url = blob_client.url + '?' + sas_token
                point.image = url

        except Exception as e:
            logging.error(e)

        Points_Serializer = InterestPointsSerializaer(Points, many=True)
        return Response(Points_Serializer.data)


    @api_view(['Post'])
    def postPointsInterest(self):
        pointInterestSerializer = InterestPointsSerializaer(data=self.data)
        if pointInterestSerializer.is_valid():
            pointInterestSerializer.save()
            return Response(pointInterestSerializer.data, status=201)
        return Response(pointInterestSerializer.errors, status=400)

    @api_view(['GET'])
    def getPointsInterest(self):
        pointsInterest = PointInterest.objects.all()
        interestPointsSerializer = InterestPointsSerializaer(pointsInterest, many=True)
        return Response(pointsInterest.data)

    @api_view(['GET'])
    def getRoadVehicle(self, id):
        if id:
            roadVehicle = RoadVehicle.objects.all().filter(road_map=id)
            roadvehicleSerializer = RoadVehicleSerializer(roadVehicle, many=True)
            return Response(roadvehicleSerializer.data)
        else:
            return Response("ID Missing")

    @api_view(['GET'])
    def getVehicles(self):
        vehicles = Vehicle.objects.all()
        vehicleSerializer = VehicleSerializer(vehicles, many=True)
        return Response(vehicleSerializer.data)

    @api_view(['POST'])
    def postVehicle(self):
        roadVehicle_serializer = VehicleSerializer(data=self.data)
        if roadVehicle_serializer.is_valid():
            roadVehicle_serializer.save()
            return Response(roadVehicle_serializer.data, status=201)
        return Response(roadVehicle_serializer.errors, status=400)

    @api_view(['DELETE'])
    def deleteVehicle(self, id):
        queryset = Vehicle.objects.get(id=id)
        queryset.delete()
        return Response("User eliminado")

    @api_view(['PUT'])
    def updateVehicle(self, id):
        Vehicle.objects.get(id=id).delete()
        roadVehicle_serializer = VehicleSerializer(data=self.data)
        if roadVehicle_serializer.is_valid():
            roadVehicle_serializer.save()
            return Response(roadVehicle_serializer.data, status=201)
        return Response(roadVehicle_serializer.errors, status=400)

    @api_view(['GET'])
    def getVehiclesId(self, id):
        vehicles = Vehicle.objects.all().filter(id=id)
        vehicleSerializer = VehicleSerializer(vehicles, many=True)
        return Response(vehicleSerializer.data)

    @api_view(['GET'])
    def getVehiclesEnterprise(self, enterprise):
        vehicles = Vehicle.objects.all().filter(enterprise=enterprise)
        vehicleSerializer = VehicleSerializer(vehicles, many=True)
        return Response(vehicleSerializer.data)

    @api_view(['POST'])
    def postRoutes(self):
        route_serializer = RoadMapSerializer(data=self.data)
        if route_serializer.is_valid():
            route_serializer.save()
            return Response(route_serializer.data, status=201)
        return Response(route_serializer.errors, status=400)

    @api_view(['DELETE'])
    def delete(self, id):
        queryset = RoadMap.objects.get(id=id)
        queryset.delete()
        return Response("Roteiro eliminado")

    @api_view(['PUT'])
    def saveDraft(self, id):
        tutorial = RoadMap.objects.get(id=id)
        tutorial_data = JSONParser().parse(self)
        tutorial_serializer = RoadMapSerializer(tutorial, data=tutorial_data)
        if tutorial_serializer.is_valid():
            tutorial_serializer.save()
            return JsonResponse(tutorial_serializer.data)
        return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['PUT'])
    def updateDriverVehicle(self, id):
        tutorial = Vehicle.objects.get(id=id)
        tutorial_data = JSONParser().parse(self)
        tutorial_serializer = VehicleSerializer(tutorial, data=tutorial_data)
        if tutorial_serializer.is_valid():
            tutorial_serializer.save()
            return JsonResponse(tutorial_serializer.data)
        return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
