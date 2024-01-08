from django.db import models

# Create your models here.

class Reserves(models.Model):
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    email = models.EmailField(max_length=62)
    date = models.DateField()
    unixStartTime = models.IntegerField() # Will need to check length
    unixEndTime = models.IntegerField() # Will need to check length
    accessCode = models.IntegerField() # Will need to check length