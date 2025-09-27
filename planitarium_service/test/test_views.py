from django.test import TestCase
from rest_framework.test import APIClient
from django.utils.timezone import now
from django.urls import reverse_lazy
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
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="adminpass"
        )
        self.user = User.objects.create_user(
            email="user@example.com", password="userpass"
        )

    def test_astronomy_show_list(self):
        AstronomyShow.objects.create(title="Galaxy Tour")
        self.client.force_authenticate(user=self.user)
        url = reverse_lazy("planitarium:astronomyshow-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["title"], "Galaxy Tour")

    def test_astronomy_show_search(self):
        AstronomyShow.objects.create(title="Star Journey")
        self.client.force_authenticate(user=self.user)
        url = reverse_lazy("planitarium:astronomyshow-list")
        response = self.client.get(f"{url}?search=Star")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_show_theme_admin_access(self):
        self.client.force_authenticate(user=self.admin)
        ShowTheme.objects.create(name="TEST")
        url = reverse_lazy("planitarium:showtheme-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["name"], "TEST")

    def test_show_theme_user_denied(self):
        self.client.force_authenticate(user=self.user)
        url = reverse_lazy("planitarium:showtheme-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_dome_list(self):
        PlanetariumDome.objects.create(name="Dome Test", rows=5, seat_in_row=10)
        self.client.force_authenticate(user=self.user)
        url = reverse_lazy("planitarium:planetariumdome-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["name"], "Dome Test")

    def test_show_session_list_with_annotation(self):
        dome = PlanetariumDome.objects.create(
            name="Dome Test", rows=5, seat_in_row=10
        )
        show = AstronomyShow.objects.create(title="Test")
        ShowSession.objects.create(
            astronomy_show=show, planetarium_dome=dome, show_time=now()
        )
        self.client.force_authenticate(user=self.user)
        url = reverse_lazy("planitarium:showsession-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("tickets_available", response.data["results"][0])

    def test_show_session_search(self):
        dome = PlanetariumDome.objects.create(
            name="Dome Test", rows=5, seat_in_row=10
        )
        show = AstronomyShow.objects.create(title="Search Test")
        ShowSession.objects.create(
            astronomy_show=show, planetarium_dome=dome, show_time=now()
        )
        self.client.force_authenticate(user=self.user)
        url = reverse_lazy("planitarium:showsession-list")
        response = self.client.get(f"{url}?search=Search")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_reservation_list(self):
        self.client.force_authenticate(user=self.user)
        Reservation.objects.create(user=self.user)
        url = reverse_lazy("planitarium:reservation-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_reservation_create_empty_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse_lazy("planitarium:reservation-list")
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 400)
