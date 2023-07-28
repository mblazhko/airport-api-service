from rest_framework import viewsets, mixins

from tracker.models import (
    Crew,
    Country,
    City,
    Facility,
    Airport,
    Route,
    Airplane,
    AirplaneType,
    Order,
    Flight,
    Passenger,
    Ticket,
)
from tracker.serializers import (
    CrewSerializer,
    CountrySerializer,
    CitySerializer,
    FacilitySerializer,
    AirportSerializer,
    AirportListSerializer,
    AirportDetailSerializer,
    RouteSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    AirplaneDetailSerializer,
    AirplaneTypeSerializer,
    OrderSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    PassengerSerializer,
    TicketSerializer,
)


def params_to_ints(qs) -> list[int]:
    """Converts a list of string IDs to a list of integers"""
    return [int(str_id) for str_id in qs.split(",")]


class CrewViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer

    def get_queryset(self):
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")
        position = self.request.query_params.get("position")

        queryset = self.queryset

        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)

        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)

        if position:
            queryset = queryset.filter(position__icontains=position)

        return queryset.distinct()

class CountryViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin
):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

    def get_queryset(self):
        name = self.request.query_params.get("name")

        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset.distinct()


class CityViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin
):
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def get_queryset(self):
        name = self.request.query_params.get("name")
        country = self.request.query_params.get("country")

        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__icontains=name)

        if country:
            queryset = queryset.filter(country=country)

        return queryset.distinct()

class FacilityViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin
):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer

    def get_queryset(self):
        name = self.request.query_params.get("name")

        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset.distinct()


class AirportViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        if self.action == "retrieve":
            return AirportDetailSerializer
        return AirportSerializer


class RouteViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class AirplaneViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "retrieve":
            return AirplaneDetailSerializer
        return AirplaneSerializer


class AirplaneTypeViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action == "retrieve":
            return OrderDetailSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FlightViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer


class PassengerViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin
):
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
