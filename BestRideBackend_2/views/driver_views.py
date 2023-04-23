from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from environs import Env
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from BestRideBackend_2.serializers import *

env = Env()
env.read_env()


class CognitoDriver:

    @api_view(['POST'])
    def recoverAccount(request):
        client = None

        try:
            response = client.forgot_password(
                ClientId=env.str("Driver_CLIENT_ID"),
                Username=request.data['email'])
            return Response(response)
        except client.exceptions.UserNotFoundException:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)

    @api_view(['POST'])
    def confirmRecoverAccount(request):
        client = None

        try:
            response = client.confirm_forgot_password(
                ClientId=env.str("Driver_CLIENT_ID"),
                Username=request.data['email'],
                ConfirmationCode=str(request.data['code']),
                Password=request.data['password'],
            )
            return Response(response)
        except client.exceptions.UserNotFoundException:
            return Response("User Not Found", status=status.HTTP_404_NOT_FOUND)

    @api_view(['POST'])
    def resend_code(request):
        client = None

        try:
            response = client.resend_confirmation_code(
                ClientId=env.str("Driver_CLIENT_ID"),
                Username=request.data['email'])

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
        cidp = None

        try:
            response_confirmUser = cidp.confirm_sign_up(
                ClientId=env.str("Driver_CLIENT_ID"),
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

    @api_view(['POST'])
    def create_account(request):
        client = None
        try:
            response_sign_up = client.sign_up(
                ClientId=env.str('Driver_CLIENT_ID'),
                Username=request.data['email'],
                Password=request.data['password'],
                UserAttributes=[
                    {
                        'Name': "custom:Name",
                        'Value': request.data['name']
                    },
                    {
                        'Name': "custom:Birth",
                        'Value': request.data['dob']
                    },
                    {
                        'Name': "email",
                        'Value': request.data['email']
                    },
                    {
                        'Name': "custom:Gender",
                        'Value': request.data['gender']
                    },
                    {
                        'Name': "custom:Adress",
                        'Value': request.data['adress']
                    },
                    {
                        'Name': "custom:City",
                        'Value': request.data['city']
                    },
                    {
                        'Name': "custom:PostalCode",
                        'Value': request.data['PostalCode']
                    },
                    {
                        'Name': "custom:Country",
                        'Value': request.data['Country']
                    },
                    {
                        'Name': "custom:NIF",
                        'Value': request.data['NIF']
                    },
                    {
                        'Name': "custom:RNATLicense",
                        'Value': request.data['RNATLicense']
                    },
                    {
                        'Name': "custom:DriverLicense",
                        'Value': request.data['DriverLicense']
                    },
                    {
                        'Name': "custom:Phone",
                        'Value': request.data['Phone']
                    },
                    {
                        'Name': "custom:Nationality",
                        'Value': request.data['Nationality']
                    },
                    {
                        'Name': "custom:CitizenCard",
                        'Value': request.data['CitizenCard']
                    },
                    {
                        'Name': "custom:ANCATNumber",
                        'Value': request.data['ANCATNumber']
                    },
                    {
                        'Name': "custom:IBAN",
                        'Value': request.data['IBAN']
                    },
                    {
                        'Name': "custom:Image",
                        'Value': request.data['Image']
                    },
                ],
            )

            jsonToDB = {
                "email": request.data['email'],
                "image": request.data['image'],
                "specialNeedSupport": request.data['specialNeedSupport'],
                "languages": request.data['languages'],
                "availableHours": request.data['availableHours'],
                "courseTaken": request.data['courseTaken'],
                "emergencyContact": request.data['emergencyContact'],
                "typeGuide": request.data['typeGuide'],
                "about": request.data['about'],
                "vehiclesCanDrive": request.data['vehiclesCanDrive'],
                "video": request.data['video'],
                "startActivity": request.data['startActivity'],
            }

            driver_serializer = DriverSerializer(data=jsonToDB)
            if driver_serializer.is_valid():
                driver_serializer.save()
                resposta = Response(driver_serializer.data, status=201)
            else:
                return Response(driver_serializer.errors, status=400)

            respostaPostDriver = dict(resposta) | response_sign_up

            return JsonResponse(respostaPostDriver)

        except client.exceptions.InvalidPasswordException:
            return Response("Invalid Password Format", status=status.HTTP_404_NOT_FOUND)
        except client.exceptions.UsernameExistsException:
            return Response("Username already Exists !", status=status.HTTP_404_NOT_FOUND)
        except client.exceptions.CodeDeliveryFailureException:
            return Response("Error on send Code !", status=status.HTTP_404_NOT_FOUND)

    @api_view(['PUT'])
    def updateUser(self, token):
        client = None

        try:
            response = client.update_user_attributes(
                UserAttributes=[
                    {
                        'Name': "Name",
                        'Value': self.data['name']
                    },
                    {
                        'Name': "Birth",
                        'Value': self.data['dob']
                    },
                    {
                        'Name': "email",
                        'Value': self.data['email']
                    },
                    {
                        'Name': "Gender",
                        'Value': self.data['gender']
                    },
                    {
                        'Name': "Adress",
                        'Value': self.data['adress']
                    },
                    {
                        'Name': "City",
                        'Value': self.data['city']
                    },
                    {
                        'Name': "PostalCode",
                        'Value': self.data['PostalCode']
                    },
                    {
                        'Name': "Country",
                        'Value': self.data['Country']
                    },
                    {
                        'Name': "NIF",
                        'Value': self.data['NIF']
                    },
                    {
                        'Name': "RNATLicense",
                        'Value': self.data['RNATLicense']
                    },
                    {
                        'Name': "DriverLicense",
                        'Value': self.data['DriverLicense']
                    },
                    {
                        'Name': "Phone",
                        'Value': self.data['Phone']
                    },
                    {
                        'Name': "Nationality",
                        'Value': self.data['Nationality']
                    },
                    {
                        'Name': "CitizenCard",
                        'Value': self.data['CitizenCard']
                    },
                    {
                        'Name': "ANCATNumber",
                        'Value': self.data['ANCATNumber']
                    },
                    {
                        'Name': "IBAN",
                        'Value': self.data['IBAN']
                    },
                    {
                        'Name': "Image",
                        'Value': self.data['Image']
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

    @api_view(['Delete'])
    def cancelAccount(self, token, id):
        client = None
        try:
            client.delete_user(
                AccessToken=token
            )

            queryset = Driver.objects.get(idDriver=id)
            queryset.delete()

            return Response("User eliminated !")
        except client.exceptions.UserNotFoundException:
            return Response("User Not Found", status=status.HTTP_400_BAD_REQUEST)

    @api_view(['POST'])
    def login(self):
        cidp = None
        try:
            login_request = cidp.initiate_auth(
                ClientId=env.str('Driver_CLIENT_ID'),
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
        cidp = None
        response = cidp.get_id(
            AccountId='YOUR AWS ACCOUNT ID',
            IdentityPoolId='us-east-1:xxxdexxx-xxdx-xxxx-ac13-xxxxf645dxxx',
            Logins={
                'accounts.google.com': 'google returned IdToken'
            })

        return Response(response)


class ViewsDriver():
    @api_view(['GET'])
    def getDriver(self, email):
        queryset = Driver.objects.all().filter(email=email)
        serialzer_class = DriverSerializer(queryset, many=True)
        return Response(serialzer_class.data)

    @api_view(['POST'])
    def postEmergencycontact(self):
        emergencyContact_serializer = EmergencyContactDriverSerializer(data=self.data)
        if emergencyContact_serializer.is_valid():
            emergencyContact_serializer.save()
            return Response(emergencyContact_serializer.data, status=201)
        return Response(emergencyContact_serializer.errors, status=400)

    @api_view(['POST'])
    def postFkDrivertoEnterprise(self):
        fkDriverEnterprise_serializer = FKDriverEnterpriseSerializer(data=self.data)
        if fkDriverEnterprise_serializer.is_valid():
            fkDriverEnterprise_serializer.save()
            return Response(fkDriverEnterprise_serializer.data, status=201)
        return Response(fkDriverEnterprise_serializer.errors, status=400)

    @api_view(['GET'])
    def getFkDrivertoEnterprise(self):
        queryset = FKDriverEnterprise.objects.all().filter()
        serialzer_class = FKDriverEnterpriseSerializer(queryset, many=True)
        return Response(serialzer_class.data)

    @api_view(['DELETE'])
    def delete(self, id):
        queryset = Driver.objects.get(id=id)
        queryset.delete()
        return Response("Driver eliminado")

    @api_view(['PUT'])
    def updateDriverEnterprise(self, id):
        tutorial = Driver.objects.get(id=id)
        tutorial_data = JSONParser().parse(self)
        tutorial_serializer = DriverSerializer(tutorial, data=tutorial_data)
        if tutorial_serializer.is_valid():
            tutorial_serializer.save()
            return JsonResponse(tutorial_serializer.data)
        return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
