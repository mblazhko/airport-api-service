from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tracker.models import Flight
from tracker.serializers import (
    FlightListSerializer,
    FlightDetailSerializer,
)
from tracker.tests.model_samples import (
    sample_airplane,
    detail_url,
    sample_flight,
    sample_crew,
    sample_route,
)

FLIGHT_URL = reverse("tracker:flight-list")


class UnauthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword",
        )
        self.client.force_authenticate(self.user)

    def test_list_airplane(self):
        sample_flight()
        res = self.client.get(FLIGHT_URL)

        flight = Flight.objects.all()
        serializer = FlightListSerializer(flight, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_by_departure_time(self):
        flight1 = sample_flight()
        flight2 = sample_flight(departure_time="2020-01-02T00:00:00")

        res = self.client.get(FLIGHT_URL, {"departure_time": "2020-01-01"})

        serializer1 = FlightListSerializer(flight1)
        serializer2 = FlightListSerializer(flight2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_by_arrial_time(self):
        flight1 = sample_flight()
        flight2 = sample_flight(arrival_time="2020-01-02T00:00:00")

        res = self.client.get(FLIGHT_URL, {"arrival_time": "2020-01-03"})

        serializer1 = FlightListSerializer(flight1)
        serializer2 = FlightListSerializer(flight2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_flight_detail(self):
        flight = sample_flight()
        flight.crews.add(sample_crew())

        url = detail_url(id=flight.id, api_name="flight")
        res = self.client.get(url)

        serializer = FlightDetailSerializer(flight)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_flight_forbidden(self):
        payload = {
            "route": sample_route().id,
            "airplane": sample_airplane().id,
            "departure_time": "2020-01-01T00:00:00",
            "arrival_time": "2020-01-03T00:00:00",
            "terminal": "D",
            "gate": 10,
        }
        res = self.client.post(FLIGHT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.com",
            password="testpassword",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_airport(self):
        payload = {
            "route": sample_route().id,
            "airplane": sample_airplane().id,
            "departure_time": datetime.strptime(
                "2020-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S"
            ),
            "arrival_time": datetime.strptime(
                "2020-01-03T00:00:00", "%Y-%m-%dT%H:%M:%S"
            ),
            "crews": [sample_crew().id],
            "terminal": "D",
            "gate": 10,
        }
        res = self.client.post(FLIGHT_URL, payload)
        flight = Flight.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            if key == "airplane" or key == "route":
                self.assertEqual(payload[key], getattr(flight, key).id)
            elif key == "crews":
                crews_ids = list(flight.crews.values_list("id", flat=True))
                self.assertEqual(payload[key], crews_ids)
            else:
                self.assertEqual(payload[key], getattr(flight, key))
