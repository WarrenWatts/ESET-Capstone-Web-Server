from rest_framework import serializers
from .models import Reserves


class ReservesSerializer(serializers.ModelSerializer):
    class Meta:
        model=Reserves
        fields = [
            "unixStartTime",
            "unixEndTime",
            "accessCode",
        ]