from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from BestRideApi.serializers import *
from environs import Env

env = Env()
env.read_env()


class TravelScheduleList(generics.ListCreateAPIView):
    queryset = TravelSchedule.objects.all()
    serializer_class = TravelScheduleSerializer

class TravelScheduleGet(generics.RetrieveDestroyAPIView):
    queryset = TravelSchedule.objects.all()
    serializer_class = TravelScheduleSerializer

    @api_view(['GET'])
    def get(request,pk):
        queryset = TravelSchedule.objects.all().filter(turist_id=pk)
        serializer_class = TravelScheduleSerializer(queryset,many=True)
        return Response(serializer_class.data)



class Travels(generics.RetrieveDestroyAPIView):
    queryset = Travel.objects.all()
    serializer_class = TravelSerializer

    @api_view(['GET'])
    def getTurista(request,turist_id):
        queryset = Travel.objects.all().filter(turist_id=turist_id)
        serializer_class = TravelSerializer(queryset,many=True)
        return Response(serializer_class.data)

    @api_view(['GET'])
    def get(request):
        queryset = Travel.objects.all()
        serializer_class = TravelSerializer(queryset, many=True)
        return Response(serializer_class.data)

    @api_view(['POST'])
    def post(request):
        travel_serializer = TravelSerializer(data=request.data)
        if travel_serializer.is_valid():
            travel_serializer.save()
            travel_result = TravelSerializer()
            return Response(travel_result.data, status=201)
        return Response(travel_serializer.errors, status=400)

