from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from car_solution.models import Person, Car, Nod, Road, Stations
from car_solution.serializers import PersonModelSerializer, CarModelSerializer \
    , AllNodeModelSerializer, RoadModelSerializer, StationsModelSerializer, PersonCarTollSerializer
from django.contrib.gis.geos import GEOSGeometry, LineString
import operator
from django.db.models import Q, F, Subquery, Case, Value, When, Sum, OuterRef, Max
from functools import reduce
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware, make_aware
import datetime


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>GET DATA>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class GetPersonData(APIView):
    def get(self, request):
        query = Person.objects.all()
        serializers = PersonModelSerializer(query, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


class GetCarData(APIView):
    def get(self, request):
        query = Car.objects.all()
        serializers = CarModelSerializer(query, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


class GetAllNodeData(APIView):
    def get(self, request):
        query = Nod.objects.all()
        serializers = AllNodeModelSerializer(query, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


class GetStationsData(APIView):
    def get(self, request):
        query = Stations.objects.all()
        serializers = StationsModelSerializer(query, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


class GetRoadData(APIView):
    def get(self, request):
        query = Road.objects.all()
        serializers = RoadModelSerializer(query, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


# /////////////////////////////////POST DATA////////////////////////////////////////////////

def post_data(model, request):
    saved_data = []
    unsaved_data = []
    count = 0
    for i in range(len(request.data)):
        if model == 'person':
            request.data[i].update(last_time_toll_update='1993-06-25T04:59:40.037524Z')
            serializer = PersonModelSerializer(data=request.data[i])
        elif model == 'nod':
            serializer = AllNodeModelSerializer(data=request.data[i])
        elif model == 'road':
            serializer = RoadModelSerializer(data=request.data[i])
        elif model == 'station':
            serializer = StationsModelSerializer(data=request.data[i])
        if serializer.is_valid():
            serializer.save()
            count += 1
            saved_data.append(serializer.data)
        else:
            unsaved_data.append(serializer.data)
    if count == len(request.data):
        return Response(f"seved items:{saved_data}", status=status.HTTP_201_CREATED)
    else:
        return Response(f"unsaved items: {unsaved_data}", status=status.HTTP_400_BAD_REQUEST)


class PostPersonlData(APIView):

    def post(self, request):
        model = 'person'
        rsp = post_data(model, request)
        return rsp


class PostCarData(APIView):

    def post(self, request):
        saved_data = []
        unsaved_data = []
        count = 0
        for i in range(len(request.data)):
            car_data = request.data[i]['ownerCar']
            code = request.data[i]['national_code']
            national_code_dict = dict(national_code=str(code))
            for j in range(len(car_data)):
                car_data[j].update(national_code_dict)
                serializer = CarModelSerializer(data=car_data[j])
                if serializer.is_valid():
                    serializer.save()
                    count += 1
                    saved_data.append(serializer.data)
                else:
                    unsaved_data.append(serializer.data)
        if count == len(request.data):
            return Response(f"seved items:{saved_data}", status=status.HTTP_201_CREATED)
        else:
            return Response(f"unsaved items: {unsaved_data}", status=status.HTTP_400_BAD_REQUEST)


class PostRoadData(APIView):

    def post(self, request):
        model = 'road'
        rsp = post_data(model, request)
        return rsp


class PostNodsData(APIView):

    def post(self, request):
        model = 'nod'
        rsp = post_data(model, request)
        return rsp


class PostStationsData(APIView):

    def post(self, request):
        model = 'station'
        rsp = post_data(model, request)

        query = Stations.objects.all()
        for q in query:
            query.filter(name=q.name).update(road_geo=Road.objects.filter(geom__dwithin=(q.location,0.000025)).values('geom'))

        return rsp


# /////////////////////////////SEARCH DATA///////////////////////////////////////////////////

# big cars have crossed the streets that are less than 20 meters wide
class SearchBigCarInWidth20(APIView):
    def get(self, request):
        exepted_primary_id = []
        co = 0
        count = 0
        query = Nod.objects.filter(car__type='big').extra(select={'width': 'car_solution_road.width'},
                                                          tables=['car_solution_road'],
                                                          where=['car_solution_road.width<=20',
                                                                 'ST_within(car_solution_nod.location,car_solution_road.geom)']).order_by('car', 'date')

        for q in query:
            if co > 0:
                if width_l == q.width:
                    count += 1
                else:
                    if count > 0:
                        exepted_primary_id.append(primary_id)
                        count = 0
            primary_id = q.id
            width_l = q.width
            co += 1
        query = query.filter(reduce(operator.or_, (Q(id=x) for x in exepted_primary_id)))

        serializer = AllNodeModelSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# blue & red car
class SearchCarColor(APIView):
    def get(self, request):
        query = Car.objects.filter(color__in=['red', 'blue'])
        serializer = CarModelSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Cars belonging to people over 70 years old
class SearchCarAge(APIView):
    def get(self, request):
        query = Car.objects.filter(national_code__age__gt=70)
        serializer = CarModelSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Tolls of a person and his/her car in a certain period of time
class SearchOneCarToll(APIView):
    def get(self, request):
        co = 0
        st1 = Stations.objects.filter()
        exepted_primary_id = []
        ###127.0.0.1:8000/api/v1/search-car-toll/?idd=2,2020-06-08T04:59:40.037524Z,2022-06-08T04:59:40.037524Z
        all_param_search = request.GET['idd']
        search_list = all_param_search.split(',')
        search_id_str = search_list[0]
        search_id = int(search_id_str)
        search_date_start_str = search_list[1]
        search_date_end_str = search_list[2]
        car_idd = search_id

        search_date_start = parse_datetime(search_date_start_str)
        if not is_aware(search_date_start):
            search_date_start = make_aware(search_date_start)

        search_date_end = parse_datetime(search_date_end_str)
        if not is_aware(search_date_end):
            search_date_end = make_aware(search_date_end)

        query = Nod.objects.filter(car_id=car_idd, date__gte=search_date_start, date__lte=search_date_end).extra(
            select={'toll_per_cross': 'car_solution_stations.toll_per_cross'},
            tables=['car_solution_stations'],
            where=['ST_Dwithin(car_solution_stations.road_geo,car_solution_nod.location,0.000004)']).order_by('date')  ##('car_id','date')

        for q in query:
            station_location = st1.get(toll_per_cross=q.toll_per_cross).location
            if co > 0:
                if toll == q.toll_per_cross:
                    second_point = GEOSGeometry(q.location)
                    first_point = GEOSGeometry(first_location)
                    lines = LineString(second_point, first_point)
                    if GEOSGeometry(station_location).distance(lines) <= 0.00002:
                        exepted_primary_id.append(primary_id)
            primary_id = q.id
            toll = q.toll_per_cross
            first_location = q.location
            co += 1
        if len(query) > 0:
            query = query.filter(reduce(operator.or_, (Q(id=x) for x in exepted_primary_id)))

        total_toll = 0
        load = Car.objects.get(id=car_idd).load_valume
        if load == None:
            load = 0
        for q in query:
            toll_load = 300 * load
            total_toll += (q.toll_per_cross + toll_load)

        person_car_id2 = Person.objects.filter(car__id=car_idd).annotate(car_toll_over_period=Value(total_toll))
        serializer = PersonCarTollSerializer(person_car_id2, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# The amount of tolls for persons in the order of the amount of tolls
class SearchOwnersToll(APIView):
    def get(self, request):
        now = datetime.datetime.now()
        co = 0
        st1 = Stations.objects.filter()
        exepted_primary_id = []

        road_geo = [r.road_geo for r in Stations.objects.filter()]

        query = Nod.objects.filter(reduce(operator.or_, (Q(location__dwithin=(x, 0.00000001)) for x in road_geo))).order_by('car_id', 'date')
        max_date1 = Person.objects.aggregate(max_date=Max('last_time_toll_update')).get('max_date')
        query = Nod.objects.filter(date__gt=max_date1).extra(
            select={'toll_per_cross': 'car_solution_stations.toll_per_cross'},
            tables=['car_solution_stations'],
            where=['ST_Dwithin(car_solution_stations.road_geo,car_solution_nod.location,0.000004)']).order_by('car_id', 'date')

        for q in query:
            station_location = st1.get(toll_per_cross=q.toll_per_cross).location
            if co > 0:
                if toll == q.toll_per_cross:
                    second_point = GEOSGeometry(q.location)
                    first_point = GEOSGeometry(first_location)
                    lines = LineString(second_point, first_point)
                    if GEOSGeometry(station_location).distance(lines) <= 0.00002:
                        exepted_primary_id.append(primary_id)
            primary_id = q.id
            toll = q.toll_per_cross
            first_location = q.location
            co += 1
        if len(query) > 0:
            query = query.filter(reduce(operator.or_, (Q(id=x) for x in exepted_primary_id)))

        car_id_list = [q.car_id for q in query]
        car_id_list = list(set(car_id_list))  # hazf item hay tekrari
        for i in car_id_list:
            total_toll_over_period = 0
            load = Car.objects.get(id=i).load_valume
            if load == None:
                load = 0
            for q in query.filter(car_id=i):
                toll_load = 300 * load
                total_toll_over_period += (q.toll_per_cross + toll_load)
            print(total_toll_over_period)
            Person.objects.filter(car__id=i).update(total_toll_paid=F('total_toll_paid') + total_toll_over_period,
                                                    last_time_toll_update=now)

        resualt = Person.objects.order_by('-total_toll_paid').values('name', 'national_code', 'total_toll_paid')
        return Response(resualt, status=status.HTTP_200_OK)

# Cars that are currently 600 meters from the toll station
class SerachStationArea(APIView):
    def get(self, request):
        station_location = Stations.objects.get(name__contains='عوارضی 1').location
        first_query = Nod.objects.order_by('car_id', '-date').distinct('car_id').filter(car__type='small')
        query = Nod.objects.filter(id__in=first_query).filter(location__dwithin=(station_location, 0.0066))
        serializer = AllNodeModelSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
