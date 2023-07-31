import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify
from multiselectfield import MultiSelectField


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}({self.position})"


class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Countries"


class City(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}({self.country.name})"

    class Meta:
        ordering = ["country", "name"]
        verbose_name_plural = "Cities"


class Facility(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Facilities"


def movie_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/movies/", filename)


class Airport(models.Model):
    name = models.CharField(max_length=255)
    facilities = models.ManyToManyField(Facility, related_name="airports")
    closest_big_city = models.ForeignKey(City, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True, upload_to=movie_image_file_path)

    def __str__(self):
        return f"{self.name}({self.closest_big_city.name})"


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="depature_routes"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="arriving_routes"
    )
    distance = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source", "destination"], name="unique_route"
            )
        ]

    @property
    def full_way(self):
        return f"From {self.source.name} to {self.destination.name}"

    def __str__(self):
        return f"{self.source.name} -> {self.destination.name}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    SEAT_LETTERS_CHOICES = (
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
        ("E", "E"),
        ("F", "F"),
        ("G", "G"),
        ("H", "H"),
        ("I", "I"),
        ("J", "J"),
        ("K", "K"),
        ("L", "L"),
        ("M", "M"),
        ("N", "N"),
        ("O", "O"),
        ("P", "P"),
        ("Q", "Q"),
        ("R", "R"),
        ("S", "S"),
        ("T", "T"),
        ("U", "U"),
        ("V", "V"),
        ("W", "W"),
        ("X", "X"),
        ("Y", "Y"),
        ("Z", "Z"),
    )
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    seat_letters = MultiSelectField(
        choices=SEAT_LETTERS_CHOICES,
        max_choices=10,
        max_length=255,
    )
    facilities = models.ManyToManyField(Facility, related_name="airplanes")
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True, upload_to=movie_image_file_path)

    @property
    def capacity(self):
        return self.seats_in_row * self.rows

    def clean(self):
        super().clean()
        if len(self.seat_letters) != self.seats_in_row:
            raise ValidationError(
                "Number of selected seat letters must match seats in a row."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}({self.airplane_type.name})"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crews = models.ManyToManyField(Crew, related_name="flights")
    terminal = models.CharField(max_length=10)
    gate = models.IntegerField()

    def __str__(self):
        return (
            f"{self.route.source.name} -> {self.route.destination.name}: "
            f"{self.departure_time.strftime('%Y-%m-%d %H:%M:%S')} -> "
            f"{self.arrival_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    class Meta:
        ordering = ["departure_time"]


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    SEAT_CHOICES = (
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
        ("E", "E"),
        ("F", "F"),
        ("G", "G"),
        ("H", "H"),
        ("I", "I"),
        ("J", "J"),
        ("K", "K"),
        ("L", "L"),
        ("M", "M"),
        ("N", "N"),
        ("O", "O"),
        ("P", "P"),
        ("Q", "Q"),
        ("R", "R"),
        ("S", "S"),
        ("T", "T"),
        ("U", "U"),
        ("V", "V"),
        ("W", "W"),
        ("X", "X"),
        ("Y", "Y"),
        ("Z", "Z"),
    )
    passenger_first_name = models.CharField(
        max_length=255, verbose_name="first_name"
    )
    passenger_last_name = models.CharField(
        max_length=255, verbose_name="last_name"
    )
    seat_letter = models.CharField(max_length=7, choices=SEAT_CHOICES)
    row = models.IntegerField(validators=[MinValueValidator(1)])
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["row", "seat_letter", "flight"],
                name="unique_ticket",
            )
        ]

    @property
    def full_name(self):
        return f"{self.passenger_first_name} {self.passenger_last_name}"

    @property
    def seat(self):
        return f"{self.row}{self.seat_letter}"

    def clean(self):
        super().clean()
        if self.seat_letter not in self.flight.airplane.seat_letters:
            raise ValidationError(
                f"{self.flight.airplane.name} "
                f"does not have seat {self.seat_letter}"
                f"(available seats: {self.flight.airplane.seat_letters})"
            )
        if self.row > self.flight.airplane.rows:
            raise ValidationError(
                f"{self.flight.airplane.name} does not have row {self.row}"
                f"(maximum is {self.flight.airplane.rows})"
            )

    def __str__(self):
        return f"{self.flight.route}: {self.seat}"
