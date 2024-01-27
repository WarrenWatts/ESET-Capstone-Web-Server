"""/* Texas A&M University
** Electronic Systems Engineering Technology
** ESET-420 Engineering Technology Capstone II
** Author: Warren Watts
** File: forms.py
** --------
** The forms.py file holds Django forms and ModelForms. These two
** classes allow for the simplification and streamlining of processing
** data sent from an HTML form in a POST request.
** For more information on Django forms and ModelForms, go to 
** https://docs.djangoproject.com/en/5.0/topics/forms/ and 
** https://docs.djangoproject.com/en/5.0/topics/forms/modelforms/
*/"""



# Imports
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django import forms
from django.forms import ModelForm
from .models import Reserves
from .available import AvailabileTime
import datetime



"""/* Variable Naming Abbreviations Legend:
**
** str - string
** dict - dictionary
*/"""



# Constants
"""/* Notes:
** The message sent back to the webpage when a time that was available on the initial
** loading of the webpage is no longer available on submission of the form.
*/"""
TIME_STR = "is no longer available. Please select again."



"""/* Description:
** This function is used to validate that the date received from the
** form's POST request is within the time range available for reserving a
** room (one week).
**
** Parameters:
** date - the date sent from the form's POST request
**
** Notes:
** Although a return is not sent in the traditional sense, a ValidationError
** is raised if the date is not within the specified range. Django is able to
** keep a list of errors (in which this one would be contained if raised) that
** can then be easily accessed in the views.py file to display the error text.
**
*/"""
def validateDateRange(date):
    selectedDate = datetime.date.fromisoformat(str(date))
    start = datetime.date.today()
    sevenDays = 7

    end = start + datetime.timedelta(days = sevenDays) # Adds 7 days to the start date

    if selectedDate < start or selectedDate > end:
        raise ValidationError("This date is no longer available. Please select again.")



class ReservesForm(ModelForm):
    # The input_formats argument ensures date is in ISO format
    date = forms.DateField(input_formats = ['%Y-%m-%d'], validators = [validateDateRange])
    
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


    """/* Description:
    ** The clean() function is a built-in ModelForm function
    ** that allows for specific fields to be checked more thoroughly
    ** in a manner which you yourself can specify. In the case of this
    ** clean() function, we are using the date field from the form's POST
    ** request and the AvailableTime function to verify that both the 
    ** start time and end time actually exist. This prevents someone
    ** from attempting to edit the client-side code in order to submit times
    ** that are not increments of thirty, are no longer available, go beyond 
    ** the time limit of two hours for a reservation, or do not exist.
    **
    ** Notes:
    ** Although a return is not sent in the traditional sense, a ValidationError
    ** is raised if the either the start time or end time meets any of the criteria listed
    ** in the descritpion above. Django is able to keep a list of errors 
    ** (in which this one would be contained if raised) that can then be easily 
    ** accessed in the views.py file to display the error text.
    */"""
    # Ensures that start time and end time selected actually exist and are available
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