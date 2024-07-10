from django.db import models


# Create your models here.
class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Industry(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Organization(models.Model):
    organization_id = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    website = models.URLField()
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE, null=True, blank=True)
    description = models.CharField(max_length=255)
    year_founded = models.IntegerField()
    number_of_employees = models.IntegerField()

    def __str__(self):
        return self.name
