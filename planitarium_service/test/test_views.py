from django.test import TestCase
from rest_framework.test import APIClient
from django.utils.timezone import now
from user.models import User
from planitarium_service.models import (
    AstronomyShow,
    ShowTheme,
    PlanetariumDome,
    ShowSession,
    Reservation,
)


class ViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(email="admin@example.com", password="adminpass")
        self.user = User.objects.create_user(email="user@example.com", password="userpass")

    # AstronomyShowView
    def test_astronomy_show_list(self):
        AstronomyShow.objects.create(title="Galaxy Tour")
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/planitarium/astronomy_show/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["title"], "Galaxy Tour")

    def test_astronomy_show_search(self):
        AstronomyShow.objects.create(title="Star Journey")
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/planitarium/astronomy_show/?search=Star")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    # ShowThemeView
    def test_show_theme_admin_access(self):
        self.client.force_authenticate(user=self.admin)
        ShowTheme.objects.create(name="Cosmic")
        response = self.client.get("/api/v1/planitarium/show_theme/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["name"], "Cosmic")

    def test_show_theme_user_denied(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/planitarium/show_theme/")
        self.assertEqual(response.status_code, 403)

    # PlanetariumDomeView
    def test_dome_list(self):
        PlanetariumDome.objects.create(name="Dome A", rows=5, seat_in_row=10)
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/planitarium/planetarium_dome/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["name"], "Dome A")

    # ShowSessionView
    def test_show_session_list_with_annotation(self):
        dome = PlanetariumDome.objects.create(name="Dome B", rows=5, seat_in_row=10)
        show = AstronomyShow.objects.create(title="Moonlight")
        ShowSession.objects.create(astronomy_show=show, planetarium_dome=dome, show_time=now())
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/planitarium/show_session/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("tickets_available", response.data["results"][0])

    def test_show_session_search(self):
        dome = PlanetariumDome.objects.create(name="Dome C", rows=5, seat_in_row=10)
        show = AstronomyShow.objects.create(title="Solar Storm")
        ShowSession.objects.create(astronomy_show=show, planetarium_dome=dome, show_time=now())
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/planitarium/show_session/?search=Solar")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    # ReservationView
    def test_reservation_list(self):
        self.client.force_authenticate(user=self.user)
        Reservation.objects.create(user=self.user)
        response = self.client.get("/api/v1/planitarium/reservation/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_reservation_create_empty_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/v1/planitarium/reservation/", {})
        self.assertEqual(response.status_code, 400)

