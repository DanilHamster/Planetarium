from django.db import models
from django.conf import settings
from user.models import User


class AstronomyShow(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(
        null=True, blank=True, upload_to="astronomy/photo/"
    )

    def __str__(self):
        return self.title

    def get_image_url(self):
        if self.image:
            return self.image.url
        return f"{settings.STATIC_URL}img/placeholder.png"


class ShowTheme(models.Model):
    name = models.CharField(max_length=255)
    shows = models.ManyToManyField(AstronomyShow, related_name="themes")

    def __str__(self):
        return self.name


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seat_in_row = models.IntegerField()

    @property
    def total_seats(self):
        return self.rows * self.seat_in_row

    @property
    def size(self):
        if self.total_seats <= 72:
            return "Small"
        if 75 <= self.total_seats <= 160:
            return "Middle"
        if self.total_seats >= 160:
            return "Big"

    def __str__(self):
        return self.name

class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(AstronomyShow, on_delete=models.CASCADE, related_name="show_sessions")
    planetarium_dome = models.ForeignKey(PlanetariumDome, on_delete=models.CASCADE, related_name="dome_sessions")
    show_time = models.DateTimeField()

    def __str__(self):
        return self.astronomy_show.title

class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservation")


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    show_session = models.ForeignKey(ShowSession, on_delete=models.CASCADE, related_name="tickets")
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['show_session', 'row', 'seat'], name="unique_ticket_seat_row_ticket")
        ]
        ordering = ("seat",)

    @staticmethod
    def validate_seat(seat: int, seat_in_row: int, error_to_raise):
        if not (1 <= seat <= seat_in_row):
            raise error_to_raise({
                "seat": f"seat must be in range [1, {seat_in_row}], not {seat}"
            })
    @staticmethod
    def validate_row(row: int, rows: int, error_to_raise):
        if not (1 <= row <= rows):
            raise error_to_raise({
                "seat": f"seat must be in range [1, {rows}], not {row}"
            })

    def clean(self):
        Ticket.validate_seat(self.seat, self.show_session.planetarium_dome.seat_in_row, ValueError)
        Ticket.validate_seat(self.row, self.show_session.planetarium_dome.rows, ValueError)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )