from django.urls import path, include
from rest_framework import routers

from planitarium_service.views import AstronomyShowView, ShowThemeView, PlanetariumDomeView, ShowSessionSerializerView, \
    ReservationView

app_name = "planitarium"

router = routers.DefaultRouter()

router.register("astronomy_show", AstronomyShowView)
router.register("show_theme", ShowThemeView)
router.register("planetarium_dome", PlanetariumDomeView)
router.register("show_session_serializer", ShowSessionSerializerView)
router.register("reservation", ReservationView)




urlpatterns = [
    path("", include(router.urls))
]