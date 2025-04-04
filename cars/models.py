from django.db import models

class Car(models.Model):
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    price = models.IntegerField()
    transmission = models.CharField(max_length=50)
    mileage = models.IntegerField()
    fuelType = models.CharField(max_length=50)
    tax = models.IntegerField()
    mpg = models.FloatField()
    engineSize = models.FloatField()

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"
