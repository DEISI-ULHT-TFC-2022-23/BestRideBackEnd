from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import user_views, routes_views, views, travel_views, payments_views, comment_views, driver_views, \
    driverEnterprise_views

urlpatterns = [
    path('', views.api_root),

    # User Cognito Urls
    path('users/', user_views.user_operations.as_view(), name='users'),
    path('login/', user_views.user_operations.login),
    path('getUser/<str:token>', user_views.user_operations.getUser),
    path('recoverUser/', user_views.user_operations.recoverAccount),
    path('updateUser/<str:token>', user_views.user_operations.updateUser),
    path('changePassword/<str:token>', user_views.user_operations.changePassword),
    #path('saveUser/', user_views.user_operations.saveUser),
    path('updateImage/<str:email>', user_views.user_operations.updateImageUser),
    path('confirmRecoverUser/', user_views.user_operations.confirmRecoverAccount),
    path('verifyAccount/', user_views.user_operations.confirmAccount),
    path('resend_code/', user_views.user_operations.resend_code),
    path('cancelAccount/<str:token>', user_views.user_operations.cancelAccount),
    path('users/<int:id>/', user_views.user_operations.as_view()),
    path('socialLogin/google/', user_views.user_operations.loginGoogle),


    # User RDS Urls
    path('deleteUser/<int:id>', user_views.Users.delete),
    path('getUserid/<str:email>/', user_views.Users.get),

    # Translate Url
    path('translate/', views.TranslateAWS.translate),

    # Iteneary Urls

    path('itineray/showRoadVehicles/<int:id>', routes_views.Routes.getRoadVehicle),
    path('itineary/showRoadMap', routes_views.Routes.getRoadbyDistance),
    path('itineary/showInterestPoints', routes_views.Routes.getPointsInterest),
    #path('itineary/distance/', routes_views.Routes.distance),

    # RoadMaps/Roteiros Urls
    path('showRoadMapsCity/<str:city>', routes_views.Routes.roadMapByCity),
    path('getRoadMapsByEnterprise/<int:enterprise>', routes_views.Routes.roadMapByEnterprise),
    path('getRoadMapsById/<int:id>', routes_views.Routes.roadMapById),
    path('createRoute/', routes_views.Routes.postRoutes),
    path('updateimageRoute/<int:id>', routes_views.Routes.updateImageRoute),
    path('deleteRoute/<int:id>', routes_views.Routes.delete),
    path('saveDraft/<int:id>', routes_views.Routes.saveDraft),

    # Vehicle Urls
    path('getVehicle', routes_views.Routes.getVehicles),
    path('postVehicle', routes_views.Routes.postVehicle),
    path('deleteVehicle/<int:id>', routes_views.Routes.deleteVehicle),
    path('getVehicleByEnterprise/<int:enterprise>', routes_views.Routes.getVehiclesEnterprise),
    path('getVehicleById/<int:id>', routes_views.Routes.getVehiclesId),
    path('updateVehicle/<int:id>', routes_views.Routes.updateVehicle),
    path('updateDriverVehicle/<int:id>', routes_views.Routes.updateDriverVehicle),
    path('updateImageVehicle/<int:id>', routes_views.Routes.updateVehiclesImage),


    # Comments Urls
    path('getComments/<int:id>', comment_views.Comment.getComments),
    path('postComments/', comment_views.Comment.postComments),
    path('getAverageComments/<int:id>', comment_views.Comment.getAverageComments),

    # Travel Urls
    path('travelsSchedule/', travel_views.TravelScheduleList.as_view()),
    path('travelsSchedule/<int:pk>/', travel_views.TravelScheduleGet.get),
    path('travels/<int:turist_id>', travel_views.Travels.getTurista),
    path('getTravels/', travel_views.Travels.get),
    path('createTravel/', travel_views.Travels.post),

    # Point of Interest Urls
    path('createPointInterest/', routes_views.Routes.postPointsInterest),
    path('getPointInterest/', routes_views.Routes.getPointsInterest),
    path('updateImagePointInterest/<int:idpercurso>', routes_views.Routes.updateImagePointsInterest),

    # Payment Urls
    path('makePayment/', payments_views.Payments.make_payment),

    # Driver Urls
    path('loginDriver/', driver_views.DriverClass.login),
    path('loginGoogleDriver/', driver_views.DriverClass.loginGoogle),
    path('deleteAccountDriver/<str:token>/', driver_views.DriverClass.cancelAccount),
    path('createDriver/', driver_views.DriverClass.create_account),
    path('getCognitoDriver/<str:token>', driver_views.DriverClass.getUser),
    path('recoverDriver/', driver_views.DriverClass.recoverAccount),
    path('updateDriver/<str:token>', driver_views.DriverClass.updateDriver),
    path('changePasswordDriver/<str:token>', driver_views.DriverClass.changePassword),
    path('saveDriver/', driver_views.DriverClass.saveUser),
    path('updateImageDriver/<str:email>', driver_views.DriverClass.updateImageUser),
    path('confirmRecoverDriver/', driver_views.DriverClass.confirmRecoverAccount),
    path('verifyAccountDriver/', driver_views.DriverClass.confirmDriverAccount),
    path('getDriverInfo/<int:id>', driver_views.DriverClass.getInfoDriver),
    path('resend_codeDriver/', driver_views.DriverClass.resend_code),
    path('cancelAccountDriver/<str:token>', driver_views.DriverClass.cancelAccount),
    path('getDriver/<str:email>', driver_views.ViewsDriver.getDriver),
    path('postEmergencyContact/', driver_views.ViewsDriver.postEmergencycontact),


    # Driver/Enterprise FK Urls
    path('postFKDriverEnterprise/', driver_views.ViewsDriver.postFkDrivertoEnterprise),
    path('getFKDriverEnterprise', driver_views.ViewsDriver.getFkDrivertoEnterprise),

    # Driver Enterprise Urls
    path('loginEnterprise/', driverEnterprise_views.Enterprise.login),
    path('loginGoogleDriverEnterprise/', driverEnterprise_views.Enterprise.loginGoogle),
    path('deleteAccountDriverEnterprise/<str:token>/<int:id>',
         driverEnterprise_views.Enterprise.cancelAccount),
    path('createDriverEnterprise/', driverEnterprise_views.Enterprise.create_account),
    path('getCognitoDriverEnterprise/<str:token>', driverEnterprise_views.Enterprise.getUser),
    path('recoverDriverEnterprise/', driverEnterprise_views.Enterprise.recoverAccount),
    path('updateDriverEnterprise/<str:token>', driverEnterprise_views.Enterprise.updateUser),
    path('changePasswordDriverEnterprise/<str:token>', driverEnterprise_views.Enterprise.changePassword),
    path('saveDriverEnterprise/', driverEnterprise_views.Enterprise.saveUser),
    path('updateImageDriverEnterprise/<str:email>', driverEnterprise_views.Enterprise.updateImageUser),
    path('confirmRecoverDriverEnterprise/', driverEnterprise_views.Enterprise.confirmRecoverAccount),
    path('verifyAccountDriverEnterprise/', driverEnterprise_views.Enterprise.confirmAccount),
    path('resend_codeDriverEnterprise/', driverEnterprise_views.Enterprise.resend_code),
    path('cancelAccountDriverEnterprise/', driverEnterprise_views.Enterprise.cancelAccount),
    path('getEmpresa/', driverEnterprise_views.DriverEnterprise.getDriverEmpresa),
    path('getEmpresaId/<str:email>', driverEnterprise_views.DriverEnterprise.getDriverEmpresa),
    path('updateDriverEnterprise/<int:id>', driver_views.ViewsDriver.updateDriverEnterprise),

]
