import string
import random
import os
import datetime
import jwt

from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from environs import Env
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from BestRideApi.serializers import *
from django.db import IntegrityError
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.forms.models import model_to_dict
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from django.db.utils import IntegrityError
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient
from BestRideApi.views.user_views import generate_recovery_code, send_recovery_code_email

env = Env()
env.read_env()

import boto3

boto3.setup_default_session(region_name=env.str('REGION_NAME_DEFAULT'))


class DriverClass():

    @api_view(['POST'])
    def recoverAccount(request):
        try:
            email = request.data['email']
            driver = Driver.objects.get(email=email)

            # Gerar um código de recuperação de conta
            recover_account_code = generate_recovery_code()  # Você deve implementar essa função
            driver.recover_account_code = recover_account_code
            driver.save()

            # Enviar um email com o código de recuperação de conta
            send_recovery_code_email(email, recover_account_code)  # Você deve implementar essa função

            return Response("Recovery code email sent", status=status.HTTP_200_OK)

        except Driver.DoesNotExist:
            return Response("Driver Not Found", status=status.HTTP_404_NOT_FOUND)
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

            # Buscar o motorista pelo código de recuperação
            driver = Driver.objects.get(recover_account_code=code)

            # Se o motorista não for encontrado, retornar um erro
            if driver is None:
                return Response("Invalid recovery code", status=status.HTTP_404_NOT_FOUND)

            # Definir a nova senha para o motorista
            driver.set_password(password)

            # Resetar o código de recuperação para None
            driver.recover_account_code = None

            # Salvar o motorista
            driver.save()

            return Response({"message": "Account recovered successfully"}, status=status.HTTP_200_OK)
        except Driver.DoesNotExist:
            return Response("Driver Not Found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @api_view(['POST'])
    def resend_code(request):
        email = request.data['email']
        try:
            driver = Driver.objects.get(email=email)
            if driver.is_active:
                return Response({"message": "Conta já ativa"})
            stored_code = driver.verification_code
            send_confirmation_email(email, stored_code)
            return Response("email sent", status=status.HTTP_200_OK)
        except Driver.DoesNotExist:
            return Response({"error": "Driver not found"}, status=status.HTTP_404_NOT_FOUND)

    @api_view(['POST'])
    def confirmDriverAccount(request):
        email = request.data['email']
        code = request.data['code']

        try:
            driver = Driver.objects.get(email=email)
            if driver.is_active:
                return Response({"message": "Conta já ativa"})
            stored_code = driver.verification_code

            if stored_code == code:
                driver.is_active = True
                driver.save()
                return Response({"message": "Driver confirmed successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Código de confirmação inválido"}, status=status.HTTP_400_BAD_REQUEST)
        except Driver.DoesNotExist:
            return Response({"error": "Driver not found"}, status=status.HTTP_404_NOT_FOUND)

    @api_view(['GET'])
    def getUser(request, token):
        try:

            decoded = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=["HS256"])
            driver_id = decoded['driver_id']
            driver = Driver.objects.get(idDriver=driver_id)

            serializer = DriverSerializer(driver)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Driver.DoesNotExist:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @api_view(['GET'])
    def getInfoDriver(request, id):
        try:

            driver = Driver.objects.get(idDriver=id)

            data = {
                'name': driver.name,
                'profile_image': driver.profile_image,
                'languages': driver.languages
            }

            return Response(data, status=status.HTTP_200_OK)

        except Driver.DoesNotExist:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @api_view(['POST'])
    def create_account(request):
        if request.method == 'POST':
            try:
                driver_data = JSONParser().parse(request)

                # Criação do EmergencyContactDriver
                emergency_contact_data = driver_data['emergency_contact']
                emergency_contact = EmergencyContactDriver(name=emergency_contact_data['name'],
                                                           phone=emergency_contact_data['phone_number'],
                                                           relation=emergency_contact_data['relation'])
                emergency_contact.save()

                driver = Driver(email=driver_data['email'],
                                name=driver_data['name'],
                                address=driver_data['address'],
                                dob=driver_data['dob'],
                                phone_number=driver_data['phone_number'],
                                gender=driver_data['gender'],
                                emergency_contact_id=emergency_contact,
                                postal_code=driver_data['postal_code'],
                                country=driver_data['country'],
                                nif=driver_data['nif'],
                                rnat_license=driver_data['RNATLicense'],
                                driver_license=driver_data['driverLicense'],
                                nationality=driver_data['nationality'],
                                course_taken=driver_data['courseTaken'],
                                citizen_card=driver_data['citizenCard'],
                                ancat_number=driver_data['ANCATNumber'],
                                iban=driver_data['IBAN'],
                                driver_type=driver_data['driverType'],
                                about=driver_data['about'],
                                video=driver_data['video'])

                driver.verification_code = generate_confirmation_code()
                driver.set_password(driver_data['password'])
                driver.save()
                send_confirmation_email(driver_data['email'], driver.verification_code)
                return JsonResponse(driver_data, status=status.HTTP_201_CREATED, safe=False)
            except KeyError as e:
                return JsonResponse(f"Invalid data. Missing key: {str(e)}", status=status.HTTP_400_BAD_REQUEST, safe=False)
            except IntegrityError as e:
                return JsonResponse(str(e), status=status.HTTP_400_BAD_REQUEST, safe=False)
            except Exception as e:
                return JsonResponse(str(e), status=status.HTTP_400_BAD_REQUEST, safe=False)

    @api_view(['PUT'])
    def updateDriver(request, token):
        try:
            driver = request.user  # Obter o driver atualmente autenticado
            data = JSONParser().parse(request)

            if 'emergency_contact' in data:
                emergency_contact_data = data.pop('emergency_contact')
                EmergencyContactDriver.objects.filter(id=driver.emergency_contact_id.id).update(
                    **emergency_contact_data)

            Driver.objects.filter(idDriver=driver.idDriver).update(**data)

            return Response({"message": "Driver updated successfully"}, status=status.HTTP_200_OK)

        except Driver.DoesNotExist:
            return Response({"error": "Driver not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @api_view(['PUT'])
    def changePassword(request, token):
        try:
            decoded = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=["HS256"])
            driver_id = decoded['driver_id']
            driver = Driver.objects.get(idDriver=driver_id)

            previous_password = request.data.get('pass', None)
            new_password = request.data.get('new_pass', None)

            if not previous_password or not new_password:
                return Response("Invalid data", status=status.HTTP_400_BAD_REQUEST)

            # Verifique se a senha atual está correta
            if not check_password(previous_password, driver.password):
                return Response("Invalid Password", status=status.HTTP_400_BAD_REQUEST)

            # Altere a senha
            driver.set_password(new_password)
            driver.save()

            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)

        except Driver.DoesNotExist:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @api_view(['POST'])
    def saveUser(request):
        if request.method == 'POST':
            tutorial_data = JSONParser().parse(request)
            tutorial_serializer = UserSerializer(data=tutorial_data)
            if tutorial_serializer.is_valid():
                tutorial_serializer.save()
                return JsonResponse(tutorial_serializer.data, status=status.HTTP_201_CREATED)
            return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['PUT'])
    def updateImageUser(request, email):
        driver = Driver.objects.get(email=email)
        storage_connection_string = env.str('AZURE_STORAGE_CONNECTION_STRING')
        blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)

        container_name = 'imagesdriver'

        try:
            blob_service_client.create_container(container_name)
        except ResourceExistsError:
            pass

        file = request.FILES['image']
        file_extension = '.' + file.name.split('.')[-1]
        file_name = f"{driver.idDriver}/{request.data.get('name')}{file_extension}"
        file_data = file.read()

        blob_client = blob_service_client.get_blob_client(container_name, file_name)
        try:
            blob_client.upload_blob(file_data, overwrite=True)
        except Exception as e:
            print(str(e))

        if(request.data.get('name') == 'profile_image'):

            driver.profile_image = blob_client.url
            driver.save()
            return Response(driver.profile_image)
        elif(request.data.get('name') == 'bi_image'):
            driver.bi_image = blob_client.url
            driver.save()
            return Response(driver.bi_image)


    @api_view(['POST'])
    def cancelAccount(request, token):
        try:
            # Decodificar o token para obter o ID do usuário
            decoded = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=["HS256"])
            driver_id = decoded['driver_id']
            driver = Driver.objects.get(idDriver=driver_id)

            # Atualizar o campo is_active
            driver.is_active = False
            driver.save()

            return Response("User account cancelled", status=status.HTTP_200_OK)

        except Driver.DoesNotExist:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @api_view(['POST'])
    def login(request):
        if request.method == 'POST':
            email = request.data.get("email")
            password = request.data.get("password")
            try:
                driver = Driver.objects.get(email=email)
            except Driver.DoesNotExist:
                return Response({"error": "Driver with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            passwordMatch = check_password(password, driver.password)
            if passwordMatch:
                payload = {
                    'driver_id': driver.idDriver,
                    'email': driver.email,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
                }

                token = jwt.encode(payload, os.environ.get('SECRET_KEY'), algorithm='HS256')
                return Response({"token": token})
            else:
                return Response({"error": "Wrong password."}, status=status.HTTP_400_BAD_REQUEST)

    def loginGoogle(request):
        boto3.setup_default_session(region_name=env.str('REGION_NAME_DEFAULT'))
        cidp = boto3.client('cognito-idp')
        response = cidp.get_id(
            AccountId='YOUR AWS ACCOUNT ID',
            IdentityPoolId='us-east-1:xxxdexxx-xxdx-xxxx-ac13-xxxxf645dxxx',
            Logins={
                'accounts.google.com': 'google returned IdToken'
            })

        return Response(response)


class ViewsDriver():
    @api_view(['GET'])
    def getDriver(request, email):
        queryset = Driver.objects.all().filter(email=email)
        serialzer_class = DriverSerializer(queryset, many=True)
        return Response(serialzer_class.data)

    @api_view(['POST'])
    def postEmergencycontact(request):
        emergencyContact_serializer = EmergencyContactDriverSerializer(data=request.data)
        if emergencyContact_serializer.is_valid():
            emergencyContact_serializer.save()
            return Response(emergencyContact_serializer.data, status=201)
        return Response(emergencyContact_serializer.errors, status=400)

    @api_view(['POST'])
    def postFkDrivertoEnterprise(request):
        fkDriverEnterprise_serializer = FKDriverEnterpriseSerializer(data=request.data)
        if fkDriverEnterprise_serializer.is_valid():
            fkDriverEnterprise_serializer.save()
            return Response(fkDriverEnterprise_serializer.data, status=201)
        return Response(fkDriverEnterprise_serializer.errors, status=400)

    @api_view(['GET'])
    def getFkDrivertoEnterprise(request):
        queryset = FKDriverEnterprise.objects.all().filter()
        serialzer_class = FKDriverEnterpriseSerializer(queryset, many=True)
        return Response(serialzer_class.data)

    @api_view(['DELETE'])
    def delete(request, id):
        queryset = Driver.objects.get(id=id)
        queryset.delete()
        return Response("Driver eliminado")

    @api_view(['PUT'])
    def updateDriverEnterprise(request, id):
        tutorial = Driver.objects.get(id=id)
        tutorial_data = JSONParser().parse(request)
        tutorial_serializer = DriverSerializer(tutorial, data=tutorial_data)
        if tutorial_serializer.is_valid():
            tutorial_serializer.save()
            return JsonResponse(tutorial_serializer.data)
        return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def generate_confirmation_code():
    code_length = 7
    characters = string.digits
    return ''.join(random.choices(characters, k=code_length))

def send_confirmation_email(email, confirmation_code):
    subject = "Confirmação de conta"
    html_content = render_to_string('confirm_email_template_driver.html', {'confirmation_code': confirmation_code})
    text_content = strip_tags(html_content)
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
    email.attach_alternative(html_content, 'text/html')
    email.send()
