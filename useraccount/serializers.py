from rest_framework import serializers

from .models import User,Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "address",
            "image",
            "about",
            "country",
            "company",
            "address_line_1",
            "headline",
            "city",
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        model = User
        fields = ("id", "name", "avatar_url","profile")