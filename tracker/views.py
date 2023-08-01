from datetime import datetime

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

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
    AirportImageSerializer,
    AirplaneImageSerializer
)


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
            queryset = queryset.filter(first_name=first_name)

        if last_name:
            queryset = queryset.filter(last_name=last_name)

        if position:
            queryset = queryset.filter(position=position)

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
            queryset = queryset.filter(name=name)

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
            queryset = queryset.filter(name=name)

        if country:
            queryset = queryset.filter(country__id=country)

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

    @staticmethod
    def _params_to_ints(qs) -> list[int]:
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        name = self.request.query_params.get("name")
        facilities = self.request.query_params.get("facilities")
        closest_big_city = self.request.query_params.get("closest_big_city")

        queryset = self.queryset

        if name:
            queryset = queryset.filter(name=name)

        if facilities:
            facilities_ids = self._params_to_ints(facilities)
            queryset = queryset.filter(facilities__id__in=facilities_ids)

        if closest_big_city:
            queryset = queryset.filter(closest_big_city__name=closest_big_city)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        if self.action == "retrieve":
            return AirportDetailSerializer
        if self.action == "upload_image":
            return AirportImageSerializer
        return AirportSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        airport = self.get_object()
        serializer = self.get_serializer(airport, data=request.data)
    
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RouteViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_queryset(self):
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        queryset = self.queryset

        if source:
            queryset = queryset.filter(source__closest_big_city__name=source)

        if destination:
            queryset = queryset.filter(
                destination__closest_big_city__name=destination
            )

        return queryset.distinct()


class AirplaneViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    @staticmethod
    def _params_to_ints(qs) -> list[int]:
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "retrieve":
            return AirplaneDetailSerializer
        if self.action == "upload_image":
            return AirplaneImageSerializer
        return AirplaneSerializer

    def get_queryset(self):
        name = self.request.query_params.get("name")
        facilities = self.request.query_params.get("facilities")
        airplane_type = self.request.query_params.get("airplane_type")

        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__icontains=name)

        if facilities:
            facilities_ids = self._params_to_ints(facilities)
            queryset = queryset.filter(facilities__id__in=facilities_ids)

        if airplane_type:
            queryset = queryset.filter(airplane_type__name=airplane_type)

        return queryset.distinct()

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)
    
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AirplaneTypeViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer

    def get_queryset(self):
        name = self.request.query_params.get("name")

        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset.distinct()


class OrderViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin
):
    queryset = Order.objects.all().prefetch_related("tickets")
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        date = self.request.query_params.get("date")

        queryset = self.queryset

        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(created_at__date=date)

        return queryset.filter(user=self.request.user)

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

    def get_queryset(self):
        departure_time = self.request.query_params.get("departure_time")
        arrival_time = self.request.query_params.get("arrival_time")

        queryset = self.queryset

        if departure_time:
            date = datetime.strptime(departure_time, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date=date)

        if arrival_time:
            date = datetime.strptime(arrival_time, "%Y-%m-%d").date()
            queryset = queryset.filter(arrival_time__date=date)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer
