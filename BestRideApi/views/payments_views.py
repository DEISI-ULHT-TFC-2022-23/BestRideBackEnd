import json
import urllib.parse
import urllib3

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


class Payments(APIView):

    @api_view(['POST'])
    def make_payment(request):
        http = urllib3.PoolManager()
        data = {
            "amount": request.data['amount'],
            "currency": "eur",
            "source": request.data['token'],
            "description": "Example charge",
        }

        data = urllib.parse.urlencode(data)

        headers = {
            'Authorization': 'Bearer ' + 'sk_test_51JUeiuImOAMxh8jbAfe6Xt8n8BQdNyjbPmO9bgVSvzyNjhv9SaqL54C2T3YJcvhyLw65539fI9zJFY3rfBqRGwOQ0084dqyi6Y',
        }

        r = http.request('POST', 'https://api.stripe.com/v1/charges', headers=headers, body=data)
        return Response({'msg': r.read()})

# TODO
""" @api_view(['POST'])
    def make_payment(request):
        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
    
        try:
            charge = stripe.Charge.create(
                amount=request.data['amount'],
                currency="eur",
                source=request.data['token'],
                description="Example charge",
            )
    
            return Response({'msg': "Payment successful."}, status=status.HTTP_200_OK)
    
        except stripe.error.StripeError as e:
            # Tratamento de erros específicos da Stripe vai aqui.
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)"""
