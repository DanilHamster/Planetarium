from django.db import transaction
from rest_framework import serializers

from planitarium_service.models import AstronomyShow, ShowTheme, PlanetariumDome, ShowSession, Ticket, Reservation


class ShowThemeSerializer(serializers.ModelSerializer):

    # shows = serializers.SlugRelatedField(
    #     many=True,
    #     queryset = AstronomyShow.objects.all(),
    #     slug_field="title"
    # )
    class Meta:
        model = ShowTheme
        fields = ("id", "name", )

class AstronomyShowSerializer(serializers.ModelSerializer):

    themes = serializers.SlugRelatedField(
        many=True,
        queryset=ShowTheme.objects.all(),
        slug_field="name"
    )

    class Meta:
        model = AstronomyShow
        fields = ("title", "themes")

class AstronomyShowRetrieveSerializer(AstronomyShowSerializer):

    class Meta:
        model = AstronomyShow
        fields = ("title", "description", "themes")


class PlanetariumDomeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlanetariumDome
        fields = ("id", "name", "rows", "seat_in_row")

class ShowSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShowSession
        fields = ("id", "astronomy_show", "planetarium_dome", "show_time")


class ShowSessionRetrieveSerializer(ShowSessionSerializer):
    astronomy_show = AstronomyShowSerializer()
    planetarium_dome = PlanetariumDomeSerializer()


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "show_session",)

    def validate(self, attrs):
        Ticket.validate_seat(
            attrs["seat"],
            attrs["show_session"].planetarium_dome.seat_in_row,
            serializers.ValidationError
        )
        Ticket.validate_seat(
            attrs["row"],
            attrs["show_session"].planetarium_dome.rows,
            serializers.ValidationError
        )
        return attrs

class ReservationSerializer(serializers.ModelSerializer):

    tickets = TicketSerializer()

    class Meta:
        model = Reservation
        fields = ("id", "created_at", "tickets",)

    def create(self, validated_data):
        with transaction.atomic:
            tickets_data = validated_data.pop('tickets')
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
            return reservation