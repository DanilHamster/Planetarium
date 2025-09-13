from django.shortcuts import render
from django.template.context_processors import request
from rest_framework import generics, mixins, viewsets, filters, status
from rest_framework.decorators import action

from planitarium_service.models import AstronomyShow, ShowTheme, PlanetariumDome, ShowSession, Reservation
from planitarium_service.serializers import AstronomyShowSerializer, ShowThemeSerializer, \
    AstronomyShowRetrieveSerializer, PlanetariumDomeSerializer, ShowSessionSerializer, ShowSessionRetrieveSerializer, \
    ReservationSerializer


class AstronomyShowView(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AstronomyShowRetrieveSerializer
        return AstronomyShowSerializer


class ShowThemeView(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer

class PlanetariumDomeView(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer

class ShowSessionSerializerView(viewsets.ModelViewSet):
    queryset = ShowSession.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ShowSessionRetrieveSerializer
        return ShowSessionSerializer


class ReservationView(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


