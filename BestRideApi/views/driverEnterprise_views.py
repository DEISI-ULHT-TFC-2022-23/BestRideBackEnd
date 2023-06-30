import datetime
import os
import random
import string

import jwt
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework import status
from rest_framework.decorators import api_view
from environs import Env
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from BestRideApi import settings
from BestRideApi.serializers import *
from BestRideApi.views.user_views import generate_recovery_code, send_recovery_code_email
from django.db import IntegrityError
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient

env = Env()
env.read_env()

import boto3
boto3.setup_default_session(region_name=env.str('REGION_NAME_DEFAULT'))


class Enterprise:
    @api_view(['POST'])
    def recoverAccount(request):
        try:
            email = request.data['email']
            company = Company.objects.get(email=email)

            # Gerar um código de recuperação de conta
            recover_account_code = generate_recovery_code()  # Você deve implementar essa função
            company.recover_account_code = recover_account_code
            company.save()

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
            company = Company.objects.get(recover_account_code=code)

            # Se o motorista não for encontrado, retornar um erro
            if company is None:
                return Response("Invalid recovery code", status=status.HTTP_404_NOT_FOUND)

            # Definir a nova senha para o motorista
            company.set_password(password)

            # Resetar o código de recuperação para None
            company.recover_account_code = None

            # Salvar o motorista
            company.save()

            return Response({"message": "Account recovered successfully"}, status=status.HTTP_200_OK)
        except Company.DoesNotExist:
            return Response("Driver Not Found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @api_view(['POST'])
    def resend_code(request):
        email = request.data['email']
        try:
            company = Company.objects.get(email=email)
            if company.is_active:
                return Response({"message": "Conta já ativa"})
            stored_code = company.verification_code
            send_confirmation_email(email, stored_code)
            return Response("email sent", status=status.HTTP_200_OK)
        except Company.DoesNotExist:
            return Response({"error": "Driver not found"}, status=status.HTTP_404_NOT_FOUND)

    @api_view(['POST'])
    def confirmAccount(request):
        email = request.data['email']
        code = request.data['code']

        try:
            company = Company.objects.get(email=email)
            if company.is_active:
                return Response({"message": "Conta já ativa"})
            stored_code = company.verification_code

            if stored_code == code:
                company.is_active = True
                company.save()
                return Response({"message": "Company confirmed successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Código de confirmação inválido"}, status=status.HTTP_400_BAD_REQUEST)
        except Company.DoesNotExist:
            return Response({"error": "Driver not found"}, status=status.HTTP_404_NOT_FOUND)

    @api_view(['GET'])
    def getUser(request,token):
        try:
            decoded = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=["HS256"])
            company_id = decoded['company_id']
            company = Company.objects.get(idCompany=company_id)

            serializer = CompanySerializer(company)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Company.DoesNotExist:
            return Response("Company Not Found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @api_view(['PUT'])
    def updateUser(request,token):
        try:
            decoded = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=["HS256"])
            company_id = decoded['company_id']
            company = Company.objects.get(idCompany=company_id)

            if 'name' in request.data:
                company.name = request.data['name']
            if 'address' in request.data:
                company.address = request.data['address']
            if 'locale' in request.data:
                company.locale = request.data['locale']  # Assumindo que "locale" é um campo no seu modelo User
            if 'country' in request.data:
                company.country = request.data['country']
            if 'postalcode' in request.data:
                company.postalcode = request.data['postalcode']
            if 'nif' in request.data:
                company.nif = request.data['nif']
            if 'phone_number' in request.data:
                company.phone_number = request.data['phone_number']

            company.save()

            return Response({"message": "Company updated successfully"}, status=status.HTTP_200_OK)

        except Company.DoesNotExist:
            return Response("Company Not Found", status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response("Invalid data", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @api_view(['PUT'])
    def changePassword(request, token):
        try:
            decoded = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=["HS256"])
            company_id = decoded['company_id']
            company = Company.objects.get(idCompany=company_id)

            previous_password = request.data.get('pass', None)
            new_password = request.data.get('new_pass', None)

            if not previous_password or not new_password:
                return Response("Invalid data", status=status.HTTP_400_BAD_REQUEST)

            # Verifique se a senha atual está correta
            if not check_password(previous_password, company.password):
                return Response("Invalid Password", status=status.HTTP_400_BAD_REQUEST)

            # Altere a senha
            company.set_password(new_password)
            company.save()

            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)

        except company.DoesNotExist:
            return Response("Company Not Found", status=status.HTTP_404_NOT_FOUND)
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
    def updateImageUser(request,email):
        company = Company.objects.get(email=email)
        storage_connection_string = env.str('AZURE_STORAGE_CONNECTION_STRING')
        blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)

        container_name = 'imagescompany'

        try:
            blob_service_client.create_container(container_name)
        except ResourceExistsError:
            pass

        file = request.FILES['image']
        file_extension = '.' + file.name.split('.')[-1]
        file_name = f"{company.idCompany}/{request.data.get('name')}{file_extension}"
        file_data = file.read()

        blob_client = blob_service_client.get_blob_client(container_name, file_name)
        try:
            blob_client.upload_blob(file_data)
        except Exception as e:
            print(str(e))


        company.image = blob_client.url
        company.save()

        company_serializer = CommentsSerializer(company)
        return Response(company_serializer.data)

    @api_view(['POST'])
    def cancelAccount(request, token):
        try:
            # Decodificar o token para obter o ID do usuário
            decoded = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=["HS256"])
            company_id = decoded['company_id']
            company = Company.objects.get(idCompany=company_id)

            # Atualizar o campo is_active
            company.is_active = False
            company.save()

            return Response("Company account cancelled", status=status.HTTP_200_OK)

        except Company.DoesNotExist:
            return Response("Company Not Found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @api_view(['POST'])
    def create_account(request):
        if request.method == 'POST':
            try:
                company = Company(
                    email=request.data['email'],
                    name=request.data['name'],
                    address=request.data['address'],
                    country=request.data['country'],
                    postal_code=request.data['postal_code'],
                    nif=request.data['nif'],
                    rnat_license=request.data['rnat_license'],
                    phone_number=request.data['phone_number']
                )
                company.verification_code = generate_confirmation_code()
                company.set_password(request.data['password'])
                company.save()
                company_serializer = CompanySerializer(instance=company)
                print("aqui")
                send_confirmation_email(request.data['email'], company.verification_code)

                return JsonResponse(company_serializer.data, status=status.HTTP_201_CREATED, safe=False)
            except KeyError as e:
                #return JsonResponse("Invalid data", status=status.HTTP_400_BAD_REQUEST, safe=False)
                return JsonResponse(str(e), status=status.HTTP_400_BAD_REQUEST, safe=False)
            except IntegrityError:
                return JsonResponse("Email already exists", status=status.HTTP_400_BAD_REQUEST, safe=False)
            except Exception as e:
                return JsonResponse(str(e), status=status.HTTP_400_BAD_REQUEST, safe=False)


    @api_view(['POST'])
    def login(request):
        if request.method == 'POST':
            email = request.data.get("email")
            password = request.data.get("password")
            try:
                company = Company.objects.get(email=email)
            except Driver.DoesNotExist:
                return Response({"error": "Company with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            passwordMatch = check_password(password, company.password)
            if passwordMatch:
                payload = {
                    'driver_id': company.idDriver,
                    'email': company.email,
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


class DriverEnterprise:

    @api_view(['GET'])
    def getDriverEmpresa(request):
        queryset = Company.objects.all()
        serialzer_class = CompanySerializer(queryset, many=True)
        return Response(serialzer_class.data)

    @api_view(['GET'])
    def getDriverEmpresa(request, email):
        queryset = Company.objects.all().filter(email=email)
        serialzer_class = CompanySerializer(queryset, many=True)
        return Response(serialzer_class.data)

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