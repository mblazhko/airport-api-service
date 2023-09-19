from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from tracker.models import Crew
from tracker.tests.model_samples import sample_crew
from tracker.serializers import CrewSerializer


CREW_URL = reverse("tracker:crew-list")


class UnauthenticatedCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(CREW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword",
        )
        self.client.force_authenticate(self.user)

    def test_list_crew(self):
        sample_crew()
        res = self.client.get(CREW_URL)

        crew = Crew.objects.all()
        serializer = CrewSerializer(crew, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_by_first_name(self):
        crew1 = sample_crew(first_name="John")
        crew2 = sample_crew(first_name="Jane")

        res = self.client.get(CREW_URL, {"first_name": "John"})

        serializer1 = CrewSerializer(crew1)
        serializer2 = CrewSerializer(crew2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_by_last_name(self):
        crew1 = sample_crew(last_name="Miller")
        crew2 = sample_crew(last_name="Black")

        res = self.client.get(CREW_URL, {"last_name": "Miller"})

        serializer1 = CrewSerializer(crew1)
        serializer2 = CrewSerializer(crew2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_by_position(self):
        crew1 = sample_crew()
        crew2 = sample_crew(position="Stewardess")

        res = self.client.get(CREW_URL, {"position": "Pilot"})

        serializer1 = CrewSerializer(crew1)
        serializer2 = CrewSerializer(crew2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_create_crew_forbidden(self):
        payload = {
            "first_name": "Henry",
            "last_name": "Jackson",
            "position": "Pilot",
        }

        res = self.client.post(CREW_URL, payload)
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

    def test_create_crew(self):
        payload = {
            "first_name": "Henry",
            "last_name": "Jackson",
            "position": "Pilot",
        }

        res = self.client.post(CREW_URL, payload)
        movie = Crew.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(movie, key))
