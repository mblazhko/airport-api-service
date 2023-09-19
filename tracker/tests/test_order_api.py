from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.utils import json

from tracker.models import Order
from tracker.serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
)
from tracker.tests.model_samples import (
    sample_order,
    detail_url,
    sample_flight,
)

ORDER_URL = reverse("tracker:order-list")


class UnauthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="vifidov384@xgh6.com",
            password="testpassword",
        )
        self.client.force_authenticate(self.user)

    def test_list_order(self):
        sample_order(user=self.user)
        res = self.client.get(ORDER_URL)

        order = Order.objects.all()
        serializer = OrderListSerializer(order, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_by_created_at_date(self):
        order1 = sample_order(user=self.user)
        order1.created_at = "2022-02-22T00:00:00"
        order1.save()
        order2 = sample_order(user=self.user)

        res = self.client.get(ORDER_URL, {"date": "2022-02-22"})

        serializer1 = OrderListSerializer(order1)
        serializer2 = OrderListSerializer(order2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_order_detail(self):
        order = sample_order(user=self.user)

        url = detail_url(id=order.id, api_name="order")
        res = self.client.get(url)

        serializer = OrderDetailSerializer(order)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_order(self):
        payload = {
            "tickets": [
                {
                    "passenger_first_name": "John",
                    "passenger_last_name": "Doe",
                    "seat_letter": "A",
                    "row": 10,
                    "flight": sample_flight().id,
                },
                {
                    "passenger_first_name": "Jane",
                    "passenger_last_name": "Smith",
                    "seat_letter": "B",
                    "row": 11,
                    "flight": sample_flight().id,
                },
            ],
        }

        res = self.client.post(
            ORDER_URL, json.dumps(payload), content_type="application/json"
        )

        self.assertIn("id", res.data, f"Response data: {res.data}")

        order = Order.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for idx, ticket_payload in enumerate(payload["tickets"]):
            ticket = order.tickets.all()[idx]
            for key in ticket_payload:
                if key == "flight":
                    self.assertEqual(ticket_payload[key], ticket.flight.id)
                else:
                    self.assertEqual(ticket_payload[key], getattr(ticket, key))

        for key in payload:
            if key == "tickets":
                continue
            elif key == "user":
                self.assertEqual(payload[key], order.user.id)
            else:
                self.assertEqual(payload[key], getattr(order, key))
