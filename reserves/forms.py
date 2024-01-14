from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django import forms
from django.forms import ModelForm
from .models import Reserves
from .available import AvailabileTime
import datetime
import re


# Constants
SUSPICIOUS_STR = "You edited the page code to try and submit something..."
TIME_STR = "is no longer available. Please select again."
NAME_REGEX = r"^[A-za-z]{1,50}$"
EMAIL_REGEX = r"^[A-Za-z\._\-0-9]*[@][A-Za-z]*[\.][a-z]{2,4}$"


# Validation functions
def validate_date_range(date):
    selectedDate = datetime.date.fromisoformat(str(date))
    start = datetime.date.today()
    end = start + datetime.timedelta(7)

    if selectedDate < start or selectedDate > end:
        raise ValidationError("This date is no longer available. Please select again.")


class ReservesForm(ModelForm):
    date = forms.DateField(input_formats=['%Y-%m-%d'], validators=[validate_date_range])
    
    class Meta:
        model = Reserves
        fields = [
            "firstName",
            "lastName",
            "email",
            "date",
            "unixStartTime",
            "unixEndTime",
            "accessCode",
        ]

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        unixStartTime = cleaned_data.get("unixStartTime")
        unixEndTime = cleaned_data.get("unixEndTime")

        if date:
            availability = AvailabileTime(
                                        datetime.date.fromisoformat(str(date)),
                                        datetime.datetime.now(),
                                    )
            
            testDict = availability.getDict()
            if int(unixStartTime) in testDict.keys():
                if int(unixEndTime) not in testDict[unixStartTime]:
                    raise ValidationError("End time {}".format(TIME_STR))
            else:
                raise ValidationError("Start time {}".format(TIME_STR))