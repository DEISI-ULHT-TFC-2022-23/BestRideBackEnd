import logging
import uuid, requests


from botocore.exceptions import ClientError
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from environs import Env


env = Env()
env.read_env()


import boto3
import os


# TODO - mudar nome da classe
class TranslateAWS():

    @api_view(['POST'])
    def translate(request):
        subscription_key = 'd282af8ef2784b829c28173a468cc593'
        endpoint = 'https://api.cognitive.microsofttranslator.com/'

        location = 'westeurope'

        constructed_url = endpoint + '/translate'

        headers = {
            'Ocp-Apim-Subscription-Key': subscription_key,
            'Ocp-Apim-Subscription-Region': location,
            'Content-Type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

        text = request.data['text']
        source_lang = request.data['sourceLang']
        target_lang = request.data['outputLang']

        params = {
            'api-version': '3.0',
            'to': target_lang,
            'from': source_lang
        }

        data = [{
            'text': text
        }]

        request = requests.post(constructed_url, params=params, headers=headers, json=data)
        response = request.json()

        response_data = {
            'translated_text': response[0]['translations'][0]['text']
        }

        return Response(response_data)

@api_view(['GET'])
def api_root(request, format=None):
    """
    API for Best Ride App
    """
    return Response({
        'Users': reverse('users', request=request, format=format),
    })
