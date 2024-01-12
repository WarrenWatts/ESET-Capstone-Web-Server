from django.core.exceptions import ValidationError
from django.forms import ModelForm
from .models import Reserves
from .available import AvailabileTime
import datetime
import re

class ReservesForm(ModelForm):
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
    

    def clean_firstName(self):
        firstName = self.cleaned_data.get("firstName")
        pattern = re.compile("^[A-za-z]{1,50}$")

        if not pattern.fullmatch(firstName):
            raise ValidationError("You edited the page code to try and submit something...")
        
        return firstName


    def clean_lastName(self):
        lastName = self.cleaned_data.get("lastName")
        pattern = re.compile("^[A-za-z]{1,50}$")

        if not pattern.fullmatch(lastName):
            raise ValidationError("You edited the page code to try and submit something...")
        
        return lastName


    def clean_email(self):
        email = self.cleaned_data.get("email")
        pattern = re.compile("^[A-Za-z\._\-0-9]*[@][A-Za-z]*[\.][a-z]{2,4}$")

        if not pattern.fullmatch(email):
            raise ValidationError("You edited the page code to try and submit something...")
        
        return email


    def clean_date(self):
        date = self.cleaned_data.get("date")
        splitDate = str(date).split("-")
        selectedDate = datetime.date(int(splitDate[0]), int(splitDate[1]), int(splitDate[2]))
        start = datetime.date.today()
        end = start + datetime.timedelta(7)

        if selectedDate < start or selectedDate > end:
            raise ValidationError("This date is no longer available for reservation. Please select again.")
        
        return date
    
    def clean_unixStartTime(self):
        return self.cleaned_data.get("unixStartTime")
            

    def clean_unixEndTime(self):
        date = self.cleaned_data.get("date")
        unixStartTime = self.cleaned_data.get("unixStartTime")
        unixEndTime = self.cleaned_data.get("unixEndTime")
        
        splitDate = str(date).split("-")
        availability = AvailabileTime(
                            datetime.date(int(splitDate[0]), int(splitDate[1]), int(splitDate[2])),
                            datetime.datetime.now()
                        )
        
        testDict = availability.getDict()
        if int(unixStartTime) in testDict.keys():
            if int(unixEndTime) not in testDict[unixStartTime]:
                raise ValidationError("End time is no longer available. Please select again.")
        else:
            raise ValidationError("Start time is no longer available. Please select again.")