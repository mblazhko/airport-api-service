from django.db import models

class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Country(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}({self.country.name})"


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}({self.closest_big_city.name})"
