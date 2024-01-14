from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import models
import datetime


# Constants
SUSPICIOUS_STR = "You edited the page code to try and submit something..."
TIME_STR = "is no longer available. Please select again."
NAME_REGEX = r"^[A-za-z]{1,50}$"
EMAIL_REGEX = r"^[A-Za-z\._\-0-9]*[@][A-Za-z]*[\.][a-z]{2,4}$"


# Create your models here.
class Reserves(models.Model):
    firstName = models.CharField(max_length=50, validators=[RegexValidator(regex=NAME_REGEX, message=SUSPICIOUS_STR)])
    lastName = models.CharField(max_length=50, validators=[RegexValidator(regex=NAME_REGEX, message=SUSPICIOUS_STR)])
    email = models.EmailField(max_length=62, validators=[RegexValidator(regex=EMAIL_REGEX, message=SUSPICIOUS_STR)])
    date = models.DateField()
    unixStartTime = models.IntegerField() # Will need to check length
    unixEndTime = models.IntegerField() # Will need to check length
    accessCode = models.IntegerField() # Will need to check length
