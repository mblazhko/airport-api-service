from rest_framework import viewsets, mixins

from tracker.models import Crew, Country, City, AirplaneFacility, AirportFacility, Airport, Route, Airplane, AirplaneType, Order, Flight, Passenger, Ticket
from tracker.serializers import CrewSerializer, CountrySerializer, \
    CitySerializer, AirplaneFacilitySerializer, AirportFacilitySerializer, \
    AirportSerializer, AirportListSerializer, AirportDetailSerializer, \
    RouteSerializer, AirplaneSerializer, AirplaneListSerializer, \
    AirplaneDetailSerializer, AirplaneTypeSerializer, OrderSerializer, \
    OrderListSerializer, OrderDetailSerializer, FlightSerializer, \
    FlightListSerializer, FlightDetailSerializer, PassengerSerializer, \
    TicketSerializer


class CrewViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class CountryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class CityViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class AirplaneFacilityViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = AirplaneFacility.objects.all()
    serializer_class = AirplaneFacilitySerializer


class AirportFacilityViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = AirportFacility.objects.all()
    serializer_class = AirportFacilitySerializer


class AirportViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return AirportListSerializer
        if self.action == 'retrieve':
            return AirportDetailSerializer
        return AirportSerializer


class RouteViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

class AirplaneViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return AirplaneListSerializer
        if self.action =='retrieve':
            return AirplaneDetailSerializer
        return AirplaneSerializer


class AirplaneTypeViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        if self.action =='retrieve':
            return OrderDetailSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FlightViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return FlightListSerializer
        if self.action =='retrieve':
            return FlightDetailSerializer
        return FlightSerializer


class PassengerViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
