from django.forms import ModelForm

from .models import Property , PropertyImages
from django import forms


class PropertyForm(ModelForm):
    class Meta:
        model = Property
        fields = (
            "title",
            "description",
            "price_per_night",
            "bedrooms",
            "bathrooms",
            "guests",
            "country",
            "country_code",
            "category",
            "image",
        )


class PropertyImagesForm(forms.ModelForm):
    class Meta:
        model = PropertyImages
        fields = ("image",)
