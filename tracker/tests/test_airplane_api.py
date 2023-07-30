from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tracker.models import Airplane
from tracker.serializers import (
    AirplaneListSerializer,
    AirplaneDetailSerializer,
)
from tracker.tests.model_samples import (
    sample_airplane,
    sample_airplane_type,
    sample_facility,
    detail_url,
)

AIRPLANE_URL = reverse("tracker:airplane-list")


class UnauthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_URL)
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
        sample_airplane()
        res = self.client.get(AIRPLANE_URL)

        airport = Airplane.objects.all()
        serializer = AirplaneListSerializer(airport, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_by_name(self):
        airplane1 = sample_airplane()
        airplane2 = sample_airplane(name="370")

        res = self.client.get(AIRPLANE_URL, {"name": "747"})

        serializer1 = AirplaneListSerializer(airplane1)
        serializer2 = AirplaneListSerializer(airplane2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_by_facility(self):
        airplane_without_facilities = sample_airplane()
        airplane_with_facilities = sample_airplane()

        facility = sample_facility()

        airplane_with_facilities.facilities.set([facility])

        res = self.client.get(AIRPLANE_URL, {"facilities": facility.id})

        serializer1 = AirplaneListSerializer(airplane_without_facilities)
        serializer2 = AirplaneListSerializer(airplane_with_facilities)

        self.assertNotIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)

    def test_filter_by_airplane_type(self):
        airplane1 = sample_airplane()
        airplane2 = sample_airplane(
            airplane_type=sample_airplane_type(name="Airbus")
        )

        res = self.client.get(AIRPLANE_URL, {"airplane_type": "Boeing"})

        serializer1 = AirplaneListSerializer(airplane1)
        serializer2 = AirplaneListSerializer(airplane2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_airplane_detail(self):
        airplane = sample_airplane()
        airplane.facilities.add(sample_facility())

        url = detail_url(id=airplane.id, api_name="airplane")
        res = self.client.get(url)

        serializer = AirplaneDetailSerializer(airplane)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airlane_forbidden(self):
        payload = {
            "name": "747-200",
            "rows": 30,
            "seats_in_row": 6,
            "seat_letters": ["A", "B", "C", "D", "E", "F"],
            "airplane_type": sample_airplane_type().id,
        }

        res = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneApiTest(TestCase):
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
            "name": "747-200",
            "rows": 30,
            "seats_in_row": 6,
            "seat_letters": ["A", "B", "C", "D", "E", "F"],
            "airplane_type": sample_airplane_type().id,
            "facilities": [sample_facility().id],
        }

        res = self.client.post(AIRPLANE_URL, payload)
        airplane = Airplane.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            if key == "airplane_type":
                self.assertEqual(payload[key], getattr(airplane, key).id)
            elif key == "facilities":
                facility_ids = list(
                    airplane.facilities.values_list("id", flat=True)
                )
                self.assertEqual(payload[key], facility_ids)
            elif key == "seat_letters":
                self.assertEqual(
                    sorted(payload[key]), sorted(getattr(airplane, key))
                )
            else:
                self.assertEqual(payload[key], getattr(airplane, key))
