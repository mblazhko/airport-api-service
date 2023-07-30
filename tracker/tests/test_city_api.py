from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tracker.models import City
from tracker.serializers import CitySerializer
from tracker.tests.model_samples import sample_country, sample_city

CITY_URL = reverse("tracker:city-list")


class UnauthenticatedCityApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(CITY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCityApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword",
        )
        self.client.force_authenticate(self.user)

    def test_list_city(self):
        sample_city()
        sample_city(name="Lviv")
        res = self.client.get(CITY_URL)

        cities = City.objects.all()
        serializer = CitySerializer(cities, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_by_name(self):
        city1 = sample_city()
        city2 = sample_city(name="Lviv")

        res = self.client.get(CITY_URL, {"name": "Kyiv"})

        serializer1 = CitySerializer(city1)
        serializer2 = CitySerializer(city2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_by_country(self):
        city1 = sample_city()
        city2 = sample_city(
            name="Berlin", country=sample_country(name="Germany")
        )

        res = self.client.get(CITY_URL, {"country": city1.country.id})

        serializer1 = CitySerializer(city1)
        serializer2 = CitySerializer(city2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_create_city_forbidden(self):
        payload = {
            "name": "Lviv",
            "country": sample_country().id
        }

        res = self.client.post(CITY_URL, payload)
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


    def test_create_city(self):
        payload = {
            "name": "Lviv",
            "country": sample_country().id,
        }

        res = self.client.post(CITY_URL, payload)
        city = City.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            if key == "country":
                self.assertEqual(payload[key], getattr(city, key).id)
            else:
                self.assertEqual(payload[key], getattr(city, key))
