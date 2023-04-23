from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from environs import Env
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from BestRideBackend_2.serializers import *

env = Env()
env.read_env()


class DriverEnterpriseCognito:
    @api_view(['POST'])
    def recoverAccount(self):
        # aqui
        client = None

        try:
            response = client.forgot_password(
                ClientId=env.str("DriverEnterprise_CLIENT_ID"),
                Username=self.data['email'])
            return Response(response)
        except client.exceptions.UserNotFoundException:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)

    @api_view(['POST'])
    def confirmRecoverAccount(self):
        # aqui
        client = None

        try:
            response = client.confirm_forgot_password(
                ClientId=env.str("DriverEnterprise_CLIENT_ID"),
                Username=self.data['email'],
                ConfirmationCode=str(self.data['code']),
                Password=self.data['password'],
            )
            return Response(response)
        except client.exceptions.UserNotFoundException:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)

    @api_view(['POST'])
    def resend_code(self):
        # aqui
        client = None

        try:
            response = client.resend_confirmation_code(
                ClientId=env.str("DriverEnterprise_CLIENT_ID"),
                Username=self.data['email'])

            return JsonResponse(response)

        except client.exceptions.TooManyRequestsException:
            return Response("Too Many Requests", status=status.HTTP_404_NOT_FOUND)
        except client.exceptions.LimitExceededException:
            return Response("Limit Exceeded", status=status.HTTP_404_NOT_FOUND)
        except client.exceptions.InvalidEmailRoleAccessPolicyException:
            return Response("Invalid Email Role", status=status.HTTP_404_NOT_FOUND)
        except client.exceptions.CodeDeliveryFailureException:
            return Response("Code not Delivered", status=status.HTTP_404_NOT_FOUND)
        except client.exceptions.UserNotFoundException:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)

    @api_view(['POST'])
    def confirmAccount(self):
        # aqui
        cidp = None

        try:
            response_confirmUser = cidp.confirm_sign_up(
                ClientId=env.str("DriverEnterprise_CLIENT_ID"),
                Username=self.data['email'],
                ConfirmationCode=self.data['code']
            )
            return Response(response_confirmUser)

        except cidp.exceptions.NotAuthorizedException:
            return Response("Not Authorized", status=status.HTTP_404_NOT_FOUND)
        except cidp.exceptions.UserNotFoundException:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)
        except cidp.exceptions.LimitExceededException:
            return Response("Limit has Exceeded", status=status.HTTP_404_NOT_FOUND)
        except cidp.exceptions.CodeMismatchException:
            return Response("Code Mismatch", status=status.HTTP_404_NOT_FOUND)
        except cidp.exceptions.ExpiredCodeException:
            return Response("Code had Expired", status=status.HTTP_404_NOT_FOUND)

    @api_view(['GET'])
    def getUser(self, token):
        # aqui
        cidp = None

        try:
            response = cidp.get_user(
                AccessToken=token
            )

            return Response(response)
        except cidp.exceptions.UserNotFoundException:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)
        except cidp.exceptions.NotAuthorizedException:
            return Response("Wrong Acess Token", status=status.HTTP_404_NOT_FOUND)

    @api_view(['PUT'])
    def updateUser(self, token):
        # aqui
        client = None

        try:
            response = client.update_user_attributes(
                UserAttributes=[
                    {
                        'Name': "name",
                        'Value': self.data['name']
                    },
                    {
                        'Name': "address",
                        'Value': self.data['address']
                    },
                    {
                        'Name': "locale",
                        'Value': self.data['locale']
                    },
                    {
                        'Name': "custom:country",
                        'Value': self.data['country']
                    },
                    {
                        'Name': "custom:postalcode",
                        'Value': self.data['postalcode']
                    },
                    {
                        'Name': "custom:nif",
                        'Value': self.data['nif']
                    },
                    {
                        'Name': "phone_number",
                        'Value': self.data['phone_number']
                    },
                ],
                AccessToken='' + token,
            )
            return Response(response)
        except client.exceptions.UserNotFoundException:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)
        except client.exceptions.UserNotConfirmedException:
            return Response("Confirm your account!", status=status.HTTP_404_NOT_FOUND)

    @api_view(['PUT'])
    def changePassword(self, token):
        # aqui
        client = None

        try:
            response = client.change_password(
                PreviousPassword=self.data['pass'],
                ProposedPassword=self.data['new_pass'],
                AccessToken=self.data['token']
            )

            return Response(response)
        except client.exceptions.InvalidPasswordException:
            return Response("Invalid Password", status=status.HTTP_404_NOT_FOUND)

    @api_view(['POST'])
    def saveUser(self):
        if self.method == 'POST':
            tutorial_data = JSONParser().parse(self)
            tutorial_serializer = UserSerializer(data=tutorial_data)
            if tutorial_serializer.is_valid():
                tutorial_serializer.save()
                return JsonResponse(tutorial_serializer.data, status=status.HTTP_201_CREATED)
            return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['PUT'])
    def updateImageUser(self, email):
        tutorial = User.objects.get(email=email)
        tutorial_data = JSONParser().parse(self)
        tutorial_serializer = UserSerializer(tutorial, data=tutorial_data)
        if tutorial_serializer.is_valid():
            tutorial_serializer.save()
            return JsonResponse(tutorial_serializer.data)
        return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['DELETE'])
    def cancelAccount(self, token, id):
        # aqui
        client = None
        try:
            client.delete_user(
                AccessToken=token
            )

            queryset = EmpresaDriver.objects.get(idEmpresaDriver=id)
            queryset.delete()

            return Response("User eliminated !")
        except client.exceptions.UserNotFoundException:
            return Response("User Not Found", status=status.HTTP_400_BAD_REQUEST)

    @api_view(['POST'])
    def create_account(self):
        # aqui
        client = None
        try:
            response_sign_up = client.sign_up(
                ClientId=env.str('DriverEnterprise_CLIENT_ID'),
                Username=self.data['email'],
                Password=self.data['password'],
                UserAttributes=[
                    {
                        'Name': "name",
                        'Value': self.data['name']
                    },
                    {
                        'Name': "address",
                        'Value': self.data['address']
                    },
                    {
                        'Name': "locale",
                        'Value': self.data['locale']
                    },
                    {
                        'Name': "custom:country",
                        'Value': self.data['country']
                    },
                    {
                        'Name': "custom:postalcode",
                        'Value': self.data['postalcode']
                    },
                    {
                        'Name': "custom:nif",
                        'Value': self.data['nif']
                    },
                    {
                        'Name': "custom:RNAT",
                        'Value': self.data['rnat']
                    },
                    {
                        'Name': "phone_number",
                        'Value': self.data['phone_number']
                    },
                ],
            )

            jsonToDB = {
                "email": self.data['email'],
                "phone": self.data['phone_number']
            }

            enterprise_serializer = EmpresaDriverSerializer(data=jsonToDB)
            if enterprise_serializer.is_valid():
                enterprise_serializer.save()
                resposta = enterprise_serializer.data.copy()
            else:
                return enterprise_serializer.errors

            respostaPostDriverEmpresa = dict(resposta) | response_sign_up

            return Response(respostaPostDriverEmpresa)

        except client.exceptions.InvalidPasswordException:
            return Response("Invalid Password Format", status=status.HTTP_404_NOT_FOUND)
        except client.exceptions.UsernameExistsException:
            return Response("Username already Exists !", status=status.HTTP_404_NOT_FOUND)
        except client.exceptions.CodeDeliveryFailureException:
            return Response("Error on send Code !", status=status.HTTP_404_NOT_FOUND)

    @api_view(['POST'])
    def login(self):
        # aqui
        cidp = None
        try:
            login_request = cidp.initiate_auth(
                ClientId=env.str('DriverEnterprise_CLIENT_ID'),
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    'USERNAME': self.data['email'],
                    'PASSWORD': self.data['password']
                }
            )

            return Response(login_request, status=status.HTTP_200_OK)

        except cidp.exceptions.NotAuthorizedException:
            return Response("Incorrect username or password", status=status.HTTP_404_NOT_FOUND)

    def loginGoogle(self):
        # aqui
        cidp = None
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
        queryset = EmpresaDriver.objects.all()
        serialzer_class = EmpresaDriverSerializer(queryset, many=True)
        return Response(serialzer_class.data)

    @api_view(['GET'])
    def getDriverEmpresa(request, email):
        queryset = EmpresaDriver.objects.all().filter(email=email)
        serialzer_class = EmpresaDriverSerializer(queryset, many=True)
        return Response(serialzer_class.data)
