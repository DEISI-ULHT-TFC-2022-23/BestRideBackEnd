# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.gis.db import models


class Travel(models.Model):
    idViagem = models.AutoField(db_column='idViagem', primary_key=True)
    Pagamento_idPagamento = models.ForeignKey('Payment', models.DO_NOTHING, db_column='Pagamento_idPagamento')
    dataViagem = models.DateField
    turist_id = models.ForeignKey('User', models.DO_NOTHING, db_column='turist_id', related_name="turistID")
    horaInicio = models.DateField
    horaFim = models.DateField
    road_map_id = models.ForeignKey('RoadMap', models.DO_NOTHING, db_column='road_map_id')
    driver_id = models.ForeignKey('Driver', models.DO_NOTHING, db_column='driver_id', related_name="driverID")

    class Meta:
        db_table = 'Travel'


class Payment(models.Model):
    idPagamento = models.AutoField(db_column='idPagamento', primary_key=True)
    modo_pagamento = models.CharField(max_length=45)

    class Meta:
        db_table = "Payment"


class TravelSchedule(models.Model):
    idAgendaViagem = models.AutoField(db_column='idAgendaViagem', primary_key=True)  # Field name made lowercase.
    turist_id = models.ForeignKey('User', models.DO_NOTHING, db_column='turist_id', related_name="turist_id")
    dataAgenda = models.DateField()
    driver_id = models.ForeignKey('User', models.DO_NOTHING, db_column='driver_id', related_name="driver_id")
    road_map_id = models.ForeignKey('RoadMap', models.DO_NOTHING, db_column='road_map_id')

    class Meta:
        db_table = 'TravelSchedule'


"""class User(models.Model):
    iduser = models.AutoField(db_column='idUser', primary_key=True)  # Field name made lowercase.
    email = models.CharField(max_length=255, blank=True, null=True)
    image = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        db_table = 'User'
        """


class City(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'City'


class UserManager(BaseUserManager):
    def get_by_natural_key(self, email):
        return self.get(email=email)


class User(AbstractBaseUser):
    idUser = models.AutoField(db_column='idUser', primary_key=True)  # Field name made lowercase.
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True, unique=True)
    image = models.CharField(max_length=4000, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    # city_id = models.ForeignKey(City, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=20, blank=True, null=True, validators=[MinLengthValidator(7)])
    recover_account_code = models.CharField(max_length=20, blank=True, null=True, validators=[MinLengthValidator(7)])
    objects = UserManager()  # Adicione essa linha

    USERNAME_FIELD = 'email'

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    class Meta:
        db_table = 'User'


class EmergencyContactDriver(models.Model):
    idEmergencyContactDrive = models.AutoField(db_column='idEmergencyContactDrive',
                                               primary_key=True)  # Field name made lowercase.
    name = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    relation = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'EmergencyContactDriver'


class Driver(AbstractBaseUser):
    idDriver = models.AutoField(db_column='idDriver', primary_key=True)  # Field name made lowercase.
    email = models.CharField(max_length=255, blank=True, null=True, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    # city_id = models.ForeignKey(City, on_delete=models.CASCADE)
    postal_code = models.CharField(max_length=15, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    nif = models.IntegerField(blank=True, null=True,
                              validators=[MinValueValidator(100000000), MaxValueValidator(999999999)])
    rnat_license = models.CharField(max_length=255, blank=True, null=True)
    driver_license = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    nationality = models.CharField(max_length=255, blank=True, null=True)
    citizen_card = models.CharField(max_length=255, blank=True, null=True)
    ancat_number = models.CharField(max_length=255, blank=True, null=True)
    iban = models.CharField(max_length=255, blank=True, null=True)
    profile_image = models.TextField(blank=True, null=True)
    bi_image = models.TextField(blank=True, null=True)
    special_need_suppport = models.CharField(max_length=255, blank=True, null=True)
    languages = models.CharField(max_length=255, blank=True, null=True)  # Falta ver como meter mais que 1
    vehicles_can_drive = models.CharField(max_length=255, blank=True, null=True)  # Falta ver como meter mais que 1
    available_hours = models.CharField(max_length=255, blank=True, null=True)  # Falta ver como gerir esta info
    course_taken = models.CharField(max_length=255, blank=True, null=True)  # Falta ver como meter mais que 1
    driver_type = models.CharField(max_length=255, blank=True, null=True)
    emergency_contact_id = models.ForeignKey(EmergencyContactDriver, models.DO_NOTHING, db_column='emergencyContact_id')
    type_guide = models.CharField(max_length=255, blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    video = models.TextField(blank=True, null=True)
    start_activity = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=20, blank=True, null=True, validators=[MinLengthValidator(7)])
    recover_account_code = models.CharField(max_length=20, blank=True, null=True, validators=[MinLengthValidator(7)])# Adicionei essa linha
    objects = UserManager()

    USERNAME_FIELD = 'email'

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    class Meta:
        db_table = 'Driver'


class FKDriverEnterprise(models.Model):
    Enterprise = models.ForeignKey('Company', models.DO_NOTHING, db_column='enterprise', null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    Driver = models.ForeignKey('Driver', models.DO_NOTHING, db_column='driver', null=True)

    class Meta:
        db_table = 'FKDriverEnterprise'


class Company(AbstractBaseUser):
    idCompany = models.AutoField(db_column='idCompany', primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    rnat_license = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True, unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    # city_id = models.ForeignKey(City, on_delete=models.CASCADE)
    postal_code = models.CharField(max_length=15, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    nif = models.IntegerField(blank=True, null=True,
                              validators=[MinValueValidator(100000000), MaxValueValidator(999999999)])
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=20, blank=True, null=True, validators=[MinLengthValidator(7)])
    recover_account_code = models.CharField(max_length=20, blank=True, null=True,
                                            validators=[MinLengthValidator(7)])
    objects = UserManager()

    USERNAME_FIELD = 'email'

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()
    class Meta:
        db_table = 'Company'


class ItinearyRouteInterestPoints(models.Model):
    id = models.BigAutoField(db_column='id', primary_key=True)
    itinearyroute_id = models.IntegerField()
    pointinterest_id = models.IntegerField()

    class Meta:
        db_table = 'itineary_route_interest_points'


class RoadMap(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    price = models.CharField(max_length=100, blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True, null=True)
    image = models.CharField(max_length=322, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    route = models.GeometryField(blank=True, null=True)
    city_id = models.ForeignKey('City', models.DO_NOTHING, db_column='city_id', null=False)
    enterprise = models.ForeignKey(Company, models.DO_NOTHING, db_column='enterprise', null=True)
    driver = models.ForeignKey(Driver, models.DO_NOTHING, db_column='driver', null=True)
    arquivado = models.CharField(max_length=100, blank=True, null=True)

    objects = UserManager()

    def to_json(self):
        return {
            'description': self.description,
            'price': self.price,
            'duration': self.duration,
            'image': self.image,
            'title': self.title,
            'route': self.route,
            'city_id': self.city_id,
            'enterprise': self.enterprise,
            'driver': self.driver,
            'arquivado': self.arquivado,
        }

    class Meta:
        db_table = 'road_map'


class RoadVehicle(models.Model):
    road_map = models.ForeignKey(RoadMap, models.DO_NOTHING, db_column='road_map')
    vehicle = models.ForeignKey('Vehicle', models.DO_NOTHING, db_column='vehicle')

    class Meta:
        db_table = 'road_vehicle'
        unique_together = (('road_map', 'vehicle'),)


class Vehicle(models.Model):
    title = models.CharField(max_length=100, blank=True)
    seats = models.IntegerField(db_column='seats')
    description = models.CharField(max_length=255, blank=True, null=True)
    image = models.CharField(max_length=4000, blank=True, null=True)
    registration = models.CharField(max_length=255, blank=True)
    enterprise = models.ForeignKey(Company, models.DO_NOTHING, db_column='enterprise')
    driver = models.ForeignKey(Driver, models.DO_NOTHING, db_column='driver', null=True)
    state = models.CharField(max_length=255, blank=True)
    arquivado = models.CharField(max_length=100, blank=True, null=True)

    objects = UserManager()

    class Meta:
        db_table = 'vehicle'


class Comments(models.Model):
    idComment = models.AutoField(db_column='id', primary_key=True)
    comment = models.CharField(max_length=350, blank=True, null=True, db_column='comment')
    pontuation = models.IntegerField(db_column='pontuation')
    road_map = models.ForeignKey(RoadMap, models.DO_NOTHING, db_column='id_road_map')
    username = models.CharField(max_length=350, blank=True, null=True, db_column='username')

    class Meta:
        db_table = 'comments'


class PointInterest(models.Model):
    idpercurso = models.AutoField(db_column='idPercurso', primary_key=True)  # Field name made lowercase.
    description = models.CharField(max_length=45, blank=True, null=True)
    location = models.GeometryField(blank=True, null=True)
    image = models.CharField(max_length=322, blank=True, null=True)
    roadMap = models.ForeignKey(RoadMap, on_delete=models.CASCADE, related_name='roadMap', null=True, blank=True,
                                db_column="roadMap_id")

    objects = UserManager()

    class Meta:
        db_table = 'Point_Interest'
