from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tracker.models import Route
from tracker.serializers import RouteSerializer
from tracker.tests.model_samples import (
    sample_airport,
    sample_city,
    sample_route,
    sample_country,
)

ROUTE_URL = reverse("tracker:route-list")


class UnauthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword",
        )
        self.client.force_authenticate(self.user)

    def test_list_route(self):
        sample_route()
        res = self.client.get(ROUTE_URL)

        route = Route.objects.all()
        serializer = RouteSerializer(route, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_by_source(self):
        route1 = sample_route()
        route2 = sample_route(
            source=sample_airport(
                name="RAI", closest_big_city=sample_city(name="Rivne")
            )
        )

        res = self.client.get(ROUTE_URL, {"source": "Kyiv"})
        serializer1 = RouteSerializer(route1)
        serializer2 = RouteSerializer(route2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_by_destination(self):
        route1 = sample_route()
        route2 = sample_route(
            destination=sample_airport(
                name="RAI", closest_big_city=sample_city(name="Rivne")
            )
        )

        res = self.client.get(ROUTE_URL, {"destination": "Lviv"})

        serializer1 = RouteSerializer(route1)
        serializer2 = RouteSerializer(route2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_create_route_forbidden(self):
        payload = {
            "source": sample_airport().id,
            "destination": sample_airport().id,
            "distance": 1000,
        }

        res = self.client.post(ROUTE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.com",
            password="testpassword",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_route(self):
        country = sample_country(name="Poland")
        city = sample_city(name="Warsaw", country=country)
        payload = {
            "source": sample_airport().id,
            "destination": sample_airport(
                name="WIA",
                closest_big_city=city,
            ).id,
            "distance": 1000,
        }

        res = self.client.post(ROUTE_URL, payload)
        route = Route.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            if key == "source" or key == "destination":
                self.assertEqual(payload[key], getattr(route, key).id)
            else:
                self.assertEqual(payload[key], getattr(route, key))
