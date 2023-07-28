from django.db import transaction
from rest_framework import serializers

from tracker.models import Airport, Crew, Country, City, Route, AirplaneType, \
    Airplane, Order, Flight, Ticket, \
    Facility


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "position")


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "name")


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ("id", "name", "country")


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = ("id", "name")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "facilities", "closest_big_city")


class AirportListSerializer(AirportSerializer):
    country = serializers.CharField(
        source="closest_big_city.country.name",
        read_only=True
    )
    facilities = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )

    class Meta:
        model = Airport
        fields = ("id", "name", "country", "closest_big_city", "facilities")


class AirportDetailSerializer(AirportSerializer):
    country = serializers.CharField(
        source="closest_big_city.country.name",
        read_only=True
    )
    facilities = FacilitySerializer(many=True, read_only=True)

    class Meta:
        model = Airport
        fields = ("id", "name", "country", "closest_big_city", "facilities")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    seat_letters = serializers.MultipleChoiceField(
        choices=Airplane.SEAT_LETTERS_CHOICES)
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type", "seat_letters", "facilities")


class AirplaneListSerializer(AirplaneSerializer):
    facilities = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )
    class Meta:
        model = Airplane
        fields = ("id", "name", "capacity", "airplane_type", "facilities")


class AirplaneDetailSerializer(AirplaneSerializer):
    facilities = FacilitySerializer(many=True, read_only=True)
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "seat_letters", "capacity", "airplane_type", "facilities")


class TicketSerializer(serializers.ModelSerializer):
    departure_time = serializers.DateTimeField(source="flight.departure_time", read_only=True)
    arrival_time = serializers.DateTimeField(source="flight.arrival_time", read_only=True)
    gate = serializers.IntegerField(source="flight.gate", read_only=True)
    terminal = serializers.CharField(source="flight.terminal", read_only=True)
    class Meta:
        model = Ticket
        fields = ("id", "passenger", "seat", "gate", "terminal", "departure_time", "arrival_time")


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets_quantity = serializers.IntegerField(
        source="tickets.count",
        read_only=True
    )
    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets_quantity")


class OrderDetailSerializer(OrderSerializer):
    tickets = TicketSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")


class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "terminal", "gate", "departure_time", "arrival_time", "crews")


class FlightListSerializer(FlightSerializer):
    crews = serializers.SlugRelatedField(many=True, read_only=True, slug_field="full_name")
    route = serializers.CharField(source="route.full_way", read_only=True)
    airplane = serializers.CharField(source="airplane.name", read_only=True)
    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "terminal", "gate", "departure_time", "arrival_time", "crews")


class FlightDetailSerializer(FlightSerializer):
    crews = CrewSerializer(many=True, read_only=True)
    route = RouteSerializer(source="route", read_only=True)
    airplane = AirplaneSerializer(source="airplane", read_only=True)