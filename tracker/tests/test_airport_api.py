from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tracker.models import Airport
from tracker.serializers import AirportListSerializer, AirportDetailSerializer
from tracker.tests.model_samples import (
    sample_airport,
    sample_facility,
    sample_city,
    detail_url,
)

AIRPORT_URL = reverse("tracker:airport-list")


class UnauthenticatedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPORT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword",
        )
        self.client.force_authenticate(self.user)

    def test_list_airport(self):
        sample_airport()
        res = self.client.get(AIRPORT_URL)

        airport = Airport.objects.all()
        serializer = AirportListSerializer(airport, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_by_name(self):
        airport1 = sample_airport()
        airport2 = sample_airport(name="LWO")

        res = self.client.get(AIRPORT_URL, {"name": "KBP"})

        serializer1 = AirportListSerializer(airport1)
        serializer2 = AirportListSerializer(airport2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_by_facility(self):
        airport_without_facilities = sample_airport()
        airport_with_facilities = sample_airport(name="LWO")

        facility = sample_facility()

        airport_with_facilities.facilities.set([facility])

        res = self.client.get(AIRPORT_URL, {"facilities": facility.id})

        serializer1 = AirportListSerializer(airport_without_facilities)
        serializer2 = AirportListSerializer(airport_with_facilities)

        self.assertNotIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)

    def test_filter_by_closest_big_city(self):
        airport1 = sample_airport()
        airport2 = sample_airport(name="LWO", closest_big_city=sample_city(name="Lviv"))

        res = self.client.get(AIRPORT_URL, {"closest_big_city": "Kyiv"})

        serializer1 = AirportListSerializer(airport1)
        serializer2 = AirportListSerializer(airport2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_airport_detail(self):
        airport = sample_airport()
        airport.facilities.add(sample_facility())

        url = detail_url(id=airport.id, api_name="airport")
        res = self.client.get(url)

        serializer = AirportDetailSerializer(airport)
        print(serializer.data)
        print(res.data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airport_forbidden(self):
        payload = {
            "name": "KBP",
            "facilities": [sample_facility().id],
            "closest_big_city": sample_city(),
        }

        res = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewApiTest(TestCase):
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
            "name": "KBP",
            "facilities": [sample_facility().id],
            "closest_big_city": sample_city().id,
        }

        res = self.client.post(AIRPORT_URL, payload)
        airport = Airport.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            if key == "closest_big_city":
                self.assertEqual(payload[key], getattr(airport, key).id)
            elif key == "facilities":
                facility_ids = list(airport.facilities.values_list("id", flat=True))
                self.assertEqual(payload[key], facility_ids)
            else:
                self.assertEqual(payload[key], getattr(airport, key))
