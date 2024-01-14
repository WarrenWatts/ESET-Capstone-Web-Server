from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django import forms
from django.forms import ModelForm
from .models import Reserves
from .available import AvailabileTime
import datetime
import re


# Constants
TIME_STR = "is no longer available. Please select again."


# Function that validates that the date is in the specified date range
def validate_date_range(date):
    selectedDate = datetime.date.fromisoformat(str(date))
    start = datetime.date.today()
    end = start + datetime.timedelta(days=7) # Adds 7 days to the start date

    if selectedDate < start or selectedDate > end:
        raise ValidationError("This date is no longer available. Please select again.")


class ReservesForm(ModelForm):
    date = forms.DateField(input_formats=['%Y-%m-%d'], validators=[validate_date_range]) # Ensures date is in ISO format + uses validator
    
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

    # Ensures that start time and end time selected actually exist and are available
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        unixStartTime = cleaned_data.get("unixStartTime")
        unixEndTime = cleaned_data.get("unixEndTime")

        if date: # Only checks start and end time if date is actually available/correctly formatted
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