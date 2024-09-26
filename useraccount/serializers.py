from rest_framework import serializers

from .models import User,Profile


class UserDetailSerializerSample(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    user = UserDetailSerializerSample()
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
            "full_name",
            "full_address",
            'user'
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        model = User
        fields = ("id", "name", "avatar_url","profile")
