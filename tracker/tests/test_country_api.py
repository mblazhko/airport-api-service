from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tracker.models import Country
from tracker.serializers import CountrySerializer
from tracker.tests.model_samples import sample_country

COUNTRY_URL = reverse("tracker:country-list")


class UnauthenticatedCountryApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(COUNTRY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCountryApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword",
        )
        self.client.force_authenticate(self.user)

    def test_list_country(self):
        sample_country()
        res = self.client.get(COUNTRY_URL)

        country = Country.objects.all()
        serializer = CountrySerializer(country, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_by_name(self):
        country1 = sample_country()
        country2 = sample_country(name="USA")

        res = self.client.get(COUNTRY_URL, {"name": "Ukraine"})

        serializer1 = CountrySerializer(country1)
        serializer2 = CountrySerializer(country2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_create_country_forbidden(self):
        payload = {
            "name": "Germany",
        }

        res = self.client.post(COUNTRY_URL, payload)
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

    def test_create_country(self):
        payload = {
            "name": "Poland",
        }

        res = self.client.post(COUNTRY_URL, payload)
        country = Country.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(country, key))
