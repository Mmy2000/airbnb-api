import uuid

from django.conf import settings
from django.db import models

from useraccount.models import User


class Property(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price_per_night = models.IntegerField()
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    guests = models.IntegerField()
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255 , blank=True , null=True)
    country_code = models.CharField(max_length=10)
    category = models.CharField(max_length=255)
    favorited = models.ManyToManyField(User, related_name="favorites", blank=True)
    image = models.ImageField(upload_to="uploads/properties")
    landlord = models.ForeignKey(
        User, related_name="properties", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def image_url(self):
        return f"{settings.WEBSITE_URL}{self.image.url}"

    class Meta:
        verbose_name = "Properties"
        verbose_name_plural = "Properties"

    def __str__(self):
        return self.title 

class PropertyImages(models.Model):
    property = models.ForeignKey(Property,related_name="property_images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="uploads/properties/property images")

    def image_url(self):
        return f"{settings.WEBSITE_URL}{self.image.url}"

    class Meta:
        verbose_name = "Property Images"
        verbose_name_plural = "Property Images"

    def __str__(self):
        return str(self.property)

class Reservation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(
        Property, related_name="reservations", on_delete=models.CASCADE
    )
    start_date = models.DateField()
    end_date = models.DateField()
    number_of_nights = models.IntegerField()
    guests = models.IntegerField()
    total_price = models.FloatField()
    created_by = models.ForeignKey(
        User, related_name="reservations", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.property)
