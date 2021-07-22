from django.urls import path
from car_solution.views import PostPersonlData,PostCarData,PostNodsData,PostRoadData,\
    SearchCarColor,SearchCarAge,SearchOwnersToll,GetAllNodeData,GetCarData,GetPersonData\
    ,GetRoadData,GetStationsData,SearchBigCarInWidth20,SearchOneCarToll,SerachStationArea,PostStationsData

urlpatterns=[

    path('get-road-data/', GetRoadData.as_view()),
    path('post-person-model/', PostPersonlData.as_view()),
    path('post-car-model/', PostCarData.as_view()),
    path('post-road-model/', PostRoadData.as_view()),
    path('post-node-model/', PostNodsData.as_view()),
    path('post-station-model/', PostStationsData.as_view()),

    path('get-car-data/',GetCarData.as_view()),
    path('get-person-data/',GetPersonData.as_view()),
    path('get-nods-data/',GetAllNodeData.as_view()),
    path('get-station-data/',GetStationsData.as_view()),

    path('search-color/', SearchCarColor.as_view()),
    path('search-age_car/', SearchCarAge.as_view()),
    path('search-car-toll/', SearchOneCarToll.as_view()),
    path('search-owners-toll/', SearchOwnersToll.as_view()),
    path('search-big-car/', SearchBigCarInWidth20.as_view()),
    path('search-station-area/', SerachStationArea.as_view()),

]