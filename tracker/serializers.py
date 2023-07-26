from rest_framework import serializers

from tracker.models import Airport, Crew, Country, City, Route, AirplaneType, \
    Airplane, Order, Flight, Ticket


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


