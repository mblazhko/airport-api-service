from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tracker.models import Facility
from tracker.serializers import FacilitySerializer
from tracker.tests.model_samples import sample_facility

FACILITY_URL = reverse("tracker:facility-list")


class UnauthenticatedFacilityApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(FACILITY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFacilityApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword",
        )
        self.client.force_authenticate(self.user)

    def test_list_facility(self):
        sample_facility()
        res = self.client.get(FACILITY_URL)

        facility = Facility.objects.all()
        serializer = FacilitySerializer(facility, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_by_name(self):
        facility1 = sample_facility()
        facility2 = sample_facility(name="Wi-fi")

        res = self.client.get(FACILITY_URL, {"name": "Lounge zone"})

        serializer1 = FacilitySerializer(facility1)
        serializer2 = FacilitySerializer(facility2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_create_facility_forbidden(self):
        payload = {
            "name": "Wi-fi",
        }

        res = self.client.post(FACILITY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCountryApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.com",
            password="testpassword",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_facility(self):
        payload = {
            "name": "Poland",
        }

        res = self.client.post(FACILITY_URL, payload)
        country = Facility.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(country, key))
