from rest_framework import serializers
from .models import Reserves


class AccessSerializer(serializers.ModelSerializer):
    class Meta:
        model=Reserves
        fields = ["accessCode"]


class RsvNameSerializer(serializers.ModelSerializer):
    class Meta:
        model=Reserves
        fields = ["unixStartTime"]