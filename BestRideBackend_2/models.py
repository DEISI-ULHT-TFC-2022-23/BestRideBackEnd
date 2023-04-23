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


class User(models.Model):
    iduser = models.AutoField(db_column='idUser', primary_key=True)  # Field name made lowercase.
    email = models.CharField(max_length=255, blank=True, null=True)
    image = models.CharField(max_length=4000, blank=True, null=True)

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


class Driver(models.Model):
    idDriver = models.AutoField(db_column='idDriver', primary_key=True)  # Field name made lowercase.
    email = models.CharField(max_length=255, blank=True, null=True)
    image = models.CharField(max_length=4000, blank=True, null=True)
    specialNeedSuppport = models.CharField(max_length=255, blank=True, null=True)
    languages = models.CharField(max_length=255, blank=True, null=True)  # Falta ver como meter mais que 1
    vehiclesCanDrive = models.CharField(max_length=255, blank=True, null=True)  # Falta ver como meter mais que 1
    availableHours = models.CharField(max_length=255, blank=True, null=True)  # Falta ver como gerir esta info
    courseTaken = models.CharField(max_length=255, blank=True, null=True)  # Falta ver como meter mais que 1
    emergencyContact_id = models.ForeignKey(EmergencyContactDriver, models.DO_NOTHING, db_column='emergencyContact_id')
    typeGuide = models.CharField(max_length=255, blank=True, null=True)
    about = models.CharField(max_length=4000, blank=True, null=True)
    video = models.CharField(max_length=4000, blank=True, null=True)
    startActivity = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'Driver'


class FKDriverEnterprise(models.Model):
    Enterprise = models.ForeignKey('EmpresaDriver', models.DO_NOTHING, db_column='enterprise', null=True)
    Driver = models.ForeignKey('Driver', models.DO_NOTHING, db_column='driver', null=True)

    class Meta:
        db_table = 'FKDriverEnterprise'


class EmpresaDriver(models.Model):
    idEmpresaDriver = models.AutoField(db_column='idEmpresaDriver', primary_key=True)  # Field name made lowercase.
    email = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        db_table = 'EmpresaDriver'


class City(models.Model):
    id = models.BigAutoField(db_column='id', primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'City'


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
    location = models.GeometryField(blank=True, null=True)
    city_id = models.ForeignKey('City', models.DO_NOTHING, db_column='city_id', null=False)
    enterprise = models.ForeignKey(EmpresaDriver, models.DO_NOTHING, db_column='enterprise', null=True)
    driver = models.ForeignKey(Driver, models.DO_NOTHING, db_column='driver', null=True)
    arquivado = models.CharField(max_length=100, blank=True, null=True)

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
    enterprise = models.ForeignKey(EmpresaDriver, models.DO_NOTHING, db_column='enterprise')
    driver = models.ForeignKey(Driver, models.DO_NOTHING, db_column='driver', null=True)
    state = models.CharField(max_length=255, blank=True)
    arquivado = models.CharField(max_length=100, blank=True, null=True)

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

    class Meta:
        db_table = 'Point_Interest'



