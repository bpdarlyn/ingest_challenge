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

    # The only publisher information we're going to need in our document
    # is the publisher name. Since publisher isn't a required field,
    # we define a properly on a model level to avoid indexing errors on
    # non-existing relation.
    @property
    def country_indexing(self):
        """Publisher for indexing.

        Used in Elasticsearch indexing.
        """
        if self.country is not None:
            return self.country.name

    @property
    def industry_indexing(self):
        """Publisher for indexing.

        Used in Elasticsearch indexing.
        """
        if self.industry is not None:
            return self.industry.name
