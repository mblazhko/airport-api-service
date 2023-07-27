from django.db import transaction
from rest_framework import serializers

from tracker.models import Airport, Crew, Country, City, Route, AirplaneType, \
    Airplane, Order, Flight, Ticket


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "name")


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "name", "country")


class AirportFacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name")


class AirplaneFacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
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
        fields = ("id", "name", "country", "closest_big_city" "facilities")


class AirportDetailSerializer(AirportSerializer):
    country = serializers.CharField(
        source="closest_big_city.country.name",
        read_only=True
    )
    facilities = AirportFacilitySerializer(many=True, read_only=True)

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
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")


class AirplaneListSerializer(AirplaneSerializer):
    facilities = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )
    class Meta:
        model = Airplane
        fields = ("id", "name", "capacity", "airplane_type", "facilities")


class AirplaneDetailSerializer(AirplaneSerializer):
    facilities = AirplaneFacilitySerializer(many=True, read_only=True)
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "seat_letter", "capacity", "airplane_type", "facilities")


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
