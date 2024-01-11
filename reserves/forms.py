from django.forms import ModelForm
from .models import Reserves

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
        pass

    def clean_lastName(self):
        pass

    def clean_email(self):
        pass

    def clean_date(self):
        pass

    def clean_unixStartTime(self):
        pass

    def clean_unixEndTime(self):
        pass