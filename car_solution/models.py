from django.db import models
from django.contrib.gis.db import models
from datetime import datetime


# Create your models here.

class Person(models.Model):
    name = models.CharField(max_length=50)
    national_code = models.CharField(primary_key=True, max_length=15)
    age = models.IntegerField()
    total_toll_paid = models.IntegerField()
    last_time_toll_update = models.DateTimeField(null=True)

    def __str__(self):
        return self.owner_name

class Car(models.Model):
    id = models.IntegerField(primary_key=True)
    national_code = models.ForeignKey('Person', on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=10)
    color = models.CharField(max_length=20)
    length = models.FloatField()
    load_valume = models.FloatField(null=True)

    def __str__(self):
        return self.id

class buffer(models.Model):
    geo = models.GeometryField(primary_key=True)

    def __str__(self):
        return self.geo

class Stations(models.Model):
    name = models.CharField(max_length=200, primary_key=True)
    toll_per_cross = models.IntegerField()
    location = models.PointField()
    road_geo = models.MultiLineStringField(null=True)

    def __str__(self):
        return self.name

class Nod(models.Model):
    car = models.ForeignKey('Car', on_delete=models.SET_NULL, null=True)
    location = models.GeometryField()
    date = models.DateTimeField(null=True)

    def __str__(self):
        return self.car

class Road(models.Model):
    name = models.CharField(max_length=200, null=True)
    width = models.FloatField(null=True)
    geom = models.MultiLineStringField(primary_key=True)

    def __str__(self):
        return self.name
