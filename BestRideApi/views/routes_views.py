import logging
import os

import urllib3
import math

from azure.core.exceptions import ResourceExistsError
from botocore.exceptions import ClientError
from django.contrib.gis.measure import Distance
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework.reverse import reverse
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from BestRideApi.serializers import *
from django.contrib.gis.geos import Point, LineString
from django.contrib.gis.geos import GEOSGeometry
from environs import Env
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas

env = Env()
env.read_env()


class Routes(APIView):


    ## POR FAZER
    @api_view(['POST'])
    def getRoadbyDistance(request):
        distanciaMax = float(request.data['distanciaMax'])  # Distância máxima em metros
        Road = RoadMap.objects.all()

        distance_dict = {}
        point = Point(request.data['lng'], request.data['lat'],
                      srid=4326)  # Inverter as coordenadas para (longitude, latitude)
        print(point)
        for rd in Road:
            linestring = rd.route

            points = list(linestring.coords)
            for p in points:
                distance = point.distance(p)
                print(distance)
                distance_dict[str(rd.title)] = distance

        filtered_road = [rd for rd in Road if distance_dict.get(str(rd.title), float('inf')) <= distanciaMax]

        Road_Serializer = RoadMapSerializer(filtered_road, many=True)
        return Response(Road_Serializer.data)


    @api_view(['GET'])
    def roadMapByCity(request, city):
        roadMap = RoadMap.objects.filter(city_id__name=city)
        roadMapSerializer = RoadMapSerializer(roadMap, many=True)
        return Response(roadMapSerializer.data)

    @api_view(['GET'])
    def roadMapByEnterprise(request, enterprise):
        roadMap = RoadMap.objects.all().filter(enterprise=enterprise)
        roadMapSerializer = RoadMapSerializer(roadMap, many=True)
        return Response(roadMapSerializer.data)

    @api_view(['GET'])
    def roadMapById(request, id):
        roadMap = RoadMap.objects.all().filter(id=id)
        roadMapSerializer = RoadMapSerializer(roadMap, many=True)
        return Response(roadMapSerializer.data[0])

    @api_view(['GET'])
    def getPointsInterest(request):
        # Create a blob service client using the Azure Storage connection string
        blob_service_client = BlobServiceClient.from_connection_string(env.str('AZURE_STORAGE_CONNECTION_STRING'))

        container_name = 'pointsinterestimages'
        # Create a container if it does not exist
        try:
            blob_service_client.create_container(container_name)
        except ResourceExistsError:
            pass

        Points = PointInterest.objects.all()

        try:
            for point in Points:
                # Generate the SAS token to read the blob
                sas_token = generate_blob_sas(account_name=blob_service_client.account_name,
                                              container_name=container_name,
                                              blob_name=point.image,
                                              account_key=blob_service_client.credential.account_key,
                                              permission=BlobSasPermissions(read=True))

                # Create the blob URL using the generated SAS token
                point.image = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{point.image}?{sas_token}"
        except Exception as ex:
            logging.error(ex)

        Points_Serializer = InterestPointsSerializer(Points, many=True)
        return Response(Points_Serializer.data)

    @api_view(['Post'])
    def postPointsInterest(request):
        pointInterestSerializer = InterestPointsSerializer(data=request.data)
        if pointInterestSerializer.is_valid():
            pointInterestSerializer.save()
            return Response(pointInterestSerializer.data, status=201)
        return Response(pointInterestSerializer.errors, status=400)

    @api_view(['PUT'])
    def updateImagePointsInterest(request, idpercurso):
        point = PointInterest.objects.get(idpercurso=idpercurso)
        storage_connection_string = env.str('AZURE_STORAGE_CONNECTION_STRING')
        blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)

        container_name = 'pointsinterestimages'

        try:
            blob_service_client.create_container(container_name)
        except ResourceExistsError:
            pass

        file = request.FILES['image']
        file_extension = '.' + file.name.split('.')[-1]
        file_name = f"{point.idpercurso}/{request.data.get('name')}{file_extension}"
        file_data = file.read()

        blob_client = blob_service_client.get_blob_client(container_name, file_name)
        try:
            blob_client.upload_blob(file_data)
        except Exception as e:
            print(str(e))

        point.image = blob_client.url
        point.save()

        point_serializer = InterestPointsSerializer(point)
        return Response(point_serializer.data)

    @api_view(['GET'])
    def getPointsInterest(request):
        pointsInterest = PointInterest.objects.all()
        interestPointsSerializer = InterestPointsSerializer(pointsInterest, many=True)
        return Response(pointsInterest.data)

    @api_view(['GET'])
    def getRoadVehicle(request, id):
        if id:
            roadVehicle = RoadVehicle.objects.all().filter(road_map=id)
            roadvehicleSerializer = RoadVehicleSerializer(roadVehicle, many=True)
            return Response(roadvehicleSerializer.data)
        else:
            return Response("ID Missing")

    @api_view(['GET'])
    def getVehicles(request):
        vehicles = Vehicle.objects.all()
        vehicleSerializer = VehicleSerializer(vehicles, many=True)
        return Response(vehicleSerializer.data)

    @api_view(['POST'])
    def postVehicle(request):
        roadVehicle_serializer = VehicleSerializer(data=request.data)
        if roadVehicle_serializer.is_valid():
            roadVehicle_serializer.save()
            return Response(roadVehicle_serializer.data, status=201)
        return Response(roadVehicle_serializer.errors, status=400)

    @api_view(['PUT'])
    def updateVehiclesImage(request, id):
        vehicles = Vehicle.objects.get(id=id)
        storage_connection_string = env.str('AZURE_STORAGE_CONNECTION_STRING')
        blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)

        container_name = 'vehiclesimages'

        try:
            blob_service_client.create_container(container_name)
        except ResourceExistsError:
            pass

        file = request.FILES['image']
        file_extension = '.' + file.name.split('.')[-1]
        file_name = f"{vehicles.id}/{request.data.get('name')}{file_extension}"
        file_data = file.read()

        blob_client = blob_service_client.get_blob_client(container_name, file_name)
        try:
            blob_client.upload_blob(file_data)
        except Exception as e:
            print(str(e))

        vehicles.image = blob_client.url
        vehicles.save()

        point_serializer = VehicleSerializer(vehicles)
        return Response(point_serializer.data)

    @api_view(['DELETE'])
    def deleteVehicle(request, id):
        queryset = Vehicle.objects.get(id=id)
        queryset.delete()
        return Response("User eliminado")

    @api_view(['PUT'])
    def updateVehicle(request, id):
        Vehicle.objects.get(id=id).delete()
        roadVehicle_serializer = VehicleSerializer(data=request.data)
        if roadVehicle_serializer.is_valid():
            roadVehicle_serializer.save()
            return Response(roadVehicle_serializer.data, status=201)
        return Response(roadVehicle_serializer.errors, status=400)

    @api_view(['GET'])
    def getVehiclesId(request, id):
        vehicles = Vehicle.objects.all().filter(id=id)
        vehicleSerializer = VehicleSerializer(vehicles, many=True)
        return Response(vehicleSerializer.data)

    @api_view(['GET'])
    def getVehiclesEnterprise(request, enterprise):
        vehicles = Vehicle.objects.all().filter(enterprise=enterprise)
        vehicleSerializer = VehicleSerializer(vehicles, many=True)
        return Response(vehicleSerializer.data)

    @api_view(['POST'])
    def postRoutes(request):
        try:
            #VAMOS PASSA A RECEBER UM ARRAY DE COORDENADAS

            circuit = LineString(request.data.get('coordenadas'))
            try:
                city = City.objects.get(id=request.data.get('city_id'))
                company = Company.objects.get(idCompany=request.data.get('company_id'))
                driver = Driver.objects.get(idDriver=request.data.get('driver_id'))
            except ObjectDoesNotExist as e:
                return JsonResponse(str(e), status=status.HTTP_404_NOT_FOUND, safe=False)

            route = RoadMap(
                description= request.data.get('description'),
                price = request.data.get('price'),
                duration = request.data.get('duration'), #ACHO QUE DEVIAMOS GUARDAR EM MILISEGUNDOS
                image =request.data.get('image'),
                title = request.data.get('title'),
                route = circuit,
                city_id = city, #VER
                enterprise = company, #VER
                driver = driver, #VER
                arquivado = request.data.get('arquivado')
            )
            route.save()
            router_serializer = RoadMapSerializer(instance=route)
            return  Response(router_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return JsonResponse(str(e), status=status.HTTP_400_BAD_REQUEST, safe=False)

    @api_view(['PUT'])
    def updateImageRoute(request, id):
        route = RoadMap.objects.get(id=id)
        storage_connection_string = env.str('AZURE_STORAGE_CONNECTION_STRING')
        blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)

        container_name = 'roadmapimages'

        try:
            blob_service_client.create_container(container_name)
        except ResourceExistsError:
            pass

        file = request.FILES['image']
        file_extension = '.' + file.name.split('.')[-1]
        file_name = f"{route.id}/{request.data.get('name')}{file_extension}"
        file_data = file.read()

        blob_client = blob_service_client.get_blob_client(container_name, file_name)
        try:
            blob_client.upload_blob(file_data)
        except Exception as e:
            print(str(e))

        route.image = blob_client.url
        route.save()

        route_serializer = RoadMapSerializer(route)
        return Response(route_serializer.data)

    @api_view(['DELETE'])
    def delete(request, id):
        queryset = RoadMap.objects.get(id=id)
        queryset.delete()
        return Response("Roteiro eliminado")

    @api_view(['PUT'])
    def saveDraft(request, id):
        tutorial = RoadMap.objects.get(id=id)
        tutorial_data = JSONParser().parse(request)
        tutorial_serializer = RoadMapSerializer(tutorial, data=tutorial_data)
        if tutorial_serializer.is_valid():
            tutorial_serializer.save()
            return JsonResponse(tutorial_serializer.data)
        return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['PUT'])
    def updateDriverVehicle(request, id):
        tutorial = Vehicle.objects.get(id=id)
        tutorial_data = JSONParser().parse(request)
        tutorial_serializer = VehicleSerializer(tutorial, data=tutorial_data)
        if tutorial_serializer.is_valid():
            tutorial_serializer.save()
            return JsonResponse(tutorial_serializer.data)
        return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
