from django.db import transaction
from rest_framework import serializers

from planitarium_service.models import AstronomyShow, ShowTheme, PlanetariumDome, ShowSession, Ticket, Reservation


class ShowThemeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShowTheme
        fields = ("id", "name", )

class AstronomyShowListSerializer(serializers.ModelSerializer):

    themes = serializers.SlugRelatedField(
        many=True,
        queryset=ShowTheme.objects.all(),
        slug_field="name"
    )

    class Meta:
        model = AstronomyShow
        fields = ("title", "themes",)

class AstronomyShowSerializer(AstronomyShowListSerializer):

    class Meta:
        model = AstronomyShow
        fields = ("title", "description", "themes")


class PlanetariumDomeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlanetariumDome
        fields = ("id", "name", "rows", "seat_in_row", "total_seats", "size")

class ShowSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShowSession
        fields = ("id", "astronomy_show", "planetarium_dome", "show_time",)


class ShowSessionListSerializer(serializers.ModelSerializer):
    astronomy_show = serializers.CharField(source="astronomy_show.title", read_only=True)
    planetarium_dome = serializers.CharField(source="planetarium_dome.name", read_only=True)
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = ShowSession
        fields = ("id", "astronomy_show", "planetarium_dome", "show_time", "tickets_available")


class ShowSessionRetrieveSerializer(ShowSessionSerializer):
    astronomy_show = AstronomyShowSerializer()
    planetarium_dome = PlanetariumDomeSerializer()


class TicketSerializer(serializers.ModelSerializer):

    show_session = serializers.CharField(source="show_session.astronomy_show.title", read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "show_session")

    def validate(self, attrs):
        Ticket.validate_seat(
            attrs["seat"],
            attrs["show_session"].planetarium_dome.seat_in_row,
            serializers.ValidationError
        )
        Ticket.validate_row(
            attrs["row"],
            attrs["show_session"].planetarium_dome.rows,
            serializers.ValidationError
        )
        return attrs


class TicketRetrieveSerializer(TicketSerializer):
    show_session = ShowSessionRetrieveSerializer()


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False)

    class Meta:
        model = Reservation
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        with transaction.atomic():
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
            return reservation

class ReservationRetrieveSerializer(serializers.ModelSerializer):
    tickets = TicketRetrieveSerializer(many=True, read_only=False)

    class Meta:
        model = Reservation
        fields = ("id", "created_at", "tickets")

