from rest_framework import serializers

from .models import Property , Reservation , PropertyImages
from useraccount.serializers import UserDetailSerializer


class PropertyImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model= PropertyImages
        fields = ["image"]

class PropertiesListSerializer(serializers.ModelSerializer):
    property_images = PropertyImagesSerializer(many=True, read_only=True)
    class Meta:
        model = Property
        fields = ("id", "title", "price_per_night", "image_url", "property_images")


class PropertiesDetailSerializer(serializers.ModelSerializer):
    landlord = UserDetailSerializer(read_only=True, many=False)
    class Meta:
        model = Property
        fields = (
            "id",
            "title",
            "description",
            "price_per_night",
            "image_url",
            "bedrooms",
            "bathrooms",
            "guests",
            "landlord",
        )


class ReservationsListSerializer(serializers.ModelSerializer):
    property = PropertiesListSerializer(read_only=True, many=False)

    class Meta:
        model = Reservation
        fields = (
            "id",
            "start_date",
            "end_date",
            "number_of_nights",
            "total_price",
            "property",
        )
