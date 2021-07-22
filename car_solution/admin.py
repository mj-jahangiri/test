from django.contrib import admin
from car_solution.models import Person, Car, Road


# Register your models here.

class AdminMode(admin.ModelAdmin):
    list_display = ['name', 'national_code', 'age', 'total_toll_paid']
    search_fields = ['name', 'national_code', 'age', 'total_toll_paid']


class CarMode(admin.ModelAdmin):
    list_display = ['id', 'national_code', 'type', 'color']
    search_fields = ['id', 'national_code', 'type', 'color']


class RoadMode(admin.ModelAdmin):
    list_display = ['name', 'geom']
    search_fields = ['name', 'geom']


admin.site.register(Person, AdminMode)
admin.site.register(Car, CarMode)
admin.site.register(Road, RoadMode)
