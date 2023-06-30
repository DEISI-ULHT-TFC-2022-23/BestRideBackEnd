import logging
import os
import datetime
import string
import random
import jwt

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from rest_framework.reverse import reverse
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from BestRideApi.serializers import *
from environs import Env
from msal import ConfidentialClientApplication
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from microsoftgraph.client import Client
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.hashers import check_password
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, parser_classes

from rest_framework_jwt.settings import api_settings
from rest_framework.permissions import IsAuthenticated

import requests

import math
import urllib3

env = Env()
env.read_env()


class user_operations(APIView):

    @api_view(['POST'])
    def recoverAccount(request):
        try:
            email = request.data['email']
            user = User.objects.get(email=email)

            # Gerar um código de recuperação de conta
            recover_account_code = generate_recovery_code()
            user.recover_account_code = recover_account_code
            user.save()

            # Enviar um email com o código de recuperação de conta
            send_recovery_code_email(email, recover_account_code)

            return Response("Recovery code email sent", status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response("Invalid data", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @api_view(['POST'])
    def confirmRecoverAccount(request):
        try:
            code = request.data.get('code')
            password = request.data.get('password')
            confirm_password = request.data.get('confirm_password')

            # Validar se a senha e a confirmação da senha são iguais
            if password != confirm_password:
                return Response("Passwords do not match", status=status.HTTP_400_BAD_REQUEST)

            # Buscar o usuário pelo código de recuperação
            user = User.objects.get(recover_account_code=code)

            # Se o usuário não for encontrado, retornar um erro
            if user is None:
                return Response("Invalid recovery code", status=status.HTTP_404_NOT_FOUND)

            # Definir a nova senha para o usuário
            user.set_password(password)

            # Resetar o código de recuperação para None
            user.recover_account_code = None

            # Salvar o usuário
            user.save()

            return Response({"message": "Account recovered successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @api_view(['POST'])
    def resend_code(request):
        email = request.data['email']
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return Response({"message": "Conta já ativa"})
            stored_code = user.verification_code
            send_confirmation_email(email, stored_code)
            return Response("email sent", status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    @api_view(['POST'])
    def confirmAccount(request):
        email = request.data['email']
        code = request.data['code']

        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return Response({"message": "Conta já ativa"})
            stored_code = user.verification_code

            if stored_code == code:
                user.is_active = True
                user.save()
                return Response({"message": "User confirmed successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Código de confirmação inválido"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    @api_view(['GET'])
    def getUser(request, token):
        try:

            decoded = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=["HS256"])
            user_id = decoded['user_id']
            user = User.objects.get(idUser=user_id)

            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @api_view(['PUT'])
    def updateUser(request, token):
        try:
            decoded = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=["HS256"])
            user_id = decoded['user_id']
            user = User.objects.get(idUser=user_id)

            if 'name' in request.data:
                user.name = request.data['name']
            if 'city' in request.data:  # Vamos supor que "locale" corresponde a "city" no seu modelo User
                user.city = request.data['city']
            if 'email' in request.data:
                user.email = request.data['email']
            if 'address' in request.data:
                user.address = request.data['address']
            user.save()

            return Response({"message": "User updated successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response("Invalid data", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @api_view(['PUT'])
    def changePassword(request, token):
        try:
            # Decodificar o token para obter o ID do usuário
            decoded = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=["HS256"])
            user_id = decoded['user_id']
            user = User.objects.get(idUser=user_id)

            previous_password = request.data.get('pass', None)
            new_password = request.data.get('new_pass', None)

            if not previous_password or not new_password:
                return Response("Invalid data", status=status.HTTP_400_BAD_REQUEST)

            # Verifique se a senha atual está correta
            if not check_password(previous_password, user.password):
                return Response("Invalid Password", status=status.HTTP_400_BAD_REQUEST)

            # Altere a senha
            user.set_password(new_password)
            user.save()

            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @api_view(['PUT'])
    def updateImageUser(request, email):
        user = User.objects.get(email=email)
        storage_connection_string = env.str('AZURE_STORAGE_CONNECTION_STRING')
        blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)

        container_name = 'images'

        try:
            blob_service_client.create_container(container_name)
        except ResourceExistsError:
            pass

        # Pega o arquivo do request
        file = request.FILES['image']
        file_extension = '.' + file.name.split('.')[-1]
        file_name = f"{user.idUser}/{request.data.get('name')}{file_extension}"
        file_data = file.read()

        # Faz o upload do arquivo para o Azure Blob Storage
        blob_client = blob_service_client.get_blob_client(container_name, file_name)
        try:
            blob_client.upload_blob(file_data)
        except Exception as e:
            print(str(e))

        # Atualiza o usuário

        user.image = blob_client.url
        user.save()

        user_serializer = UserSerializer(user)
        return Response(user_serializer.data)

    @api_view(['POST'])
    def cancelAccount(request, token):
        try:
            # Decodificar o token para obter o ID do usuário
            decoded = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=["HS256"])
            user_id = decoded['user_id']
            user = User.objects.get(idUser=user_id)

            # Atualizar o campo is_active
            user.is_active = False
            user.save()

            return Response("User account cancelled", status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        if request.method == 'POST':
            try:
                user_data = JSONParser().parse(request)
                user = User(email=user_data['email'], name=user_data['name'],
                            address=user_data['address'], image=user_data['image'], dob=user_data['dob'],
                            phone_number=user_data['phone_number'], gender=user_data['gender'],
                            postal_code=user_data['postal_code'])
                user.verification_code = generate_confirmation_code()
                user.set_password(user_data['password'])
                user.save()
                send_confirmation_email(user_data['email'], user.verification_code)
                return JsonResponse(user_data, status=status.HTTP_201_CREATED, safe=False)
            except KeyError:
                return JsonResponse("Invalid data", status=status.HTTP_400_BAD_REQUEST, safe=False)
            except IntegrityError:
                return JsonResponse("Email already exists", status=status.HTTP_400_BAD_REQUEST, safe=False)
            except Exception as e:
                return JsonResponse(str(e), status=status.HTTP_400_BAD_REQUEST, safe=False)

    @api_view(['POST'])
    def login(request):
        if request.method == 'POST':
            email = request.data.get("email")
            password = request.data.get("password")
            user = authenticate(request, email=email, password=password)
            if user is not None:
                payload = {
                    'user_id': user.idUser,
                    'email': user.email,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
                }

                token = jwt.encode(payload, os.environ.get('SECRET_KEY'), algorithm='HS256')
                return Response({"token": token})
            else:
                return Response({"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)

    # TODO - nao fazer
    @api_view(['POST'])
    def loginGoogle(request):
        try:
            # Especifique o CLIENT_ID do seu aplicativo cliente do Google
            idinfo = id_token.verify_oauth2_token(request.data['id_token'], requests.Request(), 'YOUR_GOOGLE_CLIENT_ID')

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Issuer inválido')

            # O ID do usuário é armazenado no campo de sub.
            user_id = idinfo['sub']
        except ValueError:
            return Response("Invalid token", status=status.HTTP_401_UNAUTHORIZED)

        # Aqui, você tem o ID do usuário do Google. Você pode usá-lo para autenticar o usuário em seu aplicativo
        # Depois de autenticar o usuário, você pode retornar um token JWT do Azure B2C ou outro sinal de autenticação

        return Response("User authenticated", status=status.HTTP_200_OK)


class Users(generics.RetrieveDestroyAPIView):
    @api_view(['GET'])
    def get(request, email):
        queryset = User.objects.all().filter(email=email)
        serializer_class = UserSerializer(queryset, many=True)
        return Response(serializer_class.data)

    @api_view(['DELETE'])
    def delete(request, id):
        queryset = User.objects.get(iduser=id)
        queryset.delete()
        return Response("User eliminado")


def generate_confirmation_code():
    code_length = 7
    characters = string.digits
    return ''.join(random.choices(characters, k=code_length))


def send_confirmation_email(email, confirmation_code):
    subject = "Confirmação de conta"
    html_content = render_to_string('confirm_email_template.html', {'confirmation_code': confirmation_code})
    text_content = strip_tags(html_content)
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
    email.attach_alternative(html_content, 'text/html')
    email.send()


def generate_recovery_code():
    return str(random.randint(100000, 999999))


def send_recovery_code_email(email, recovery_code):
    subject = "Confirmação de conta"
    html_content = render_to_string('recover_account_email_template.html', {'recovery_code': recovery_code})
    text_content = strip_tags(html_content)
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
    email.attach_alternative(html_content, 'text/html')
    email.send()
