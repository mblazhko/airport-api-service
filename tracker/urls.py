from django.urls import path, include
from rest_framework import routers

from tracker.views import (
    CrewViewSet,
    CountryViewSet,
    CityViewSet,
    AirportViewSet,
    RouteViewSet,
    AirplaneViewSet,
    AirplaneTypeViewSet,
    OrderViewSet,
    FlightViewSet,
    PassengerViewSet,
    TicketViewSet,
    FacilityViewSet,
)

router = routers.DefaultRouter()
router.register("crews", CrewViewSet)
router.register("countries", CountryViewSet)
router.register("cities", CityViewSet)
router.register("facilities", FacilityViewSet)
router.register("airports", AirportViewSet)
router.register("routes", RouteViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("orders", OrderViewSet)
router.register("flights", FlightViewSet)
router.register("passengers", PassengerViewSet)
router.register("tickets", TicketViewSet)

urlpatterns = [path("", include(router.urls))]


app_name = "tracker"
