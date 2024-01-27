"""/* Texas A&M University
** Electronic Systems Engineering Technology
** ESET-420 Engineering Technology Capstone II
** Author: Warren Watts
** File: serializer.py
** --------
** The serializer.py file holds information related to the Django REST framework serializer.
** Serializers allow for model instances, query sets, and other complex types to be made into
** content types such as JSON. For more information on the Django REST framework serializers, go to 
** https://www.django-rest-framework.org/api-guide/serializers/
*/"""



# Imports
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