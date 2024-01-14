from logging.handlers import RotatingFileHandler
from django.template import loader
from django.http import HttpResponse
from .available import AvailabileTime
from .forms import ReservesForm
from secrets import SystemRandom
from pathlib import Path
import datetime
import logging



# Logging setup for views.py file
mainDir = Path.cwd()
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - [Line: %(lineno)d] - %(message)s')
file_handler = RotatingFileHandler(mainDir.joinpath('reserves/reservesLogFolder/views.log'))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)



# Create your views here.
def mainPage(request):
    template = loader.get_template("reserves/index.html") 
    context = dict()
    return HttpResponse(template.render(context, request))



def loadForm(request, msgString = ""):
    dateDict = dict() # Dictionary to hold dates and their start/end times
    numDays = 7 # Number of calendar dates to search
    today = datetime.datetime.now()
    baseDate = (today.date() + datetime.timedelta(1) if (today.hour >= 22 and today.minute > 30) 
                else today.date()) # If it's after the current day's last possible start time, set the first date to the next day
    
    for x in range(numDays): # Send each date to the AvailableTime class to fill the dateDict
        available = AvailabileTime(baseDate + datetime.timedelta(days = x), today)
        dateDict.update({available.getDate() : available.getDict()}) # The key of this dictionary is the calendar date, the value is another dictionary
    
    context = {
        'myMembers' : dateDict,
        'myMessage' : msgString,
    } # The data given by Django to HTML must be in dictionary form

    template = loader.get_template("reserves/forms/form.html")
    return HttpResponse(template.render(context, request))



def checkSubmit(request):
    accessGenerator = SystemRandom() # Used to generate an access code securely
    context = dict()

    if request.method == "POST": # Only execute code if the HTTP request is POST
        updated_request = request.POST.copy()
        updated_request.update({"accessCode": accessGenerator.randint(1000000, 9999999)})
        form = ReservesForm(updated_request) # Update POST request with new accessCode field
        
        if form.is_valid(): # Causes the form fields sent to be validated. Invalid if any errors found
            form.save() # Saves form info to the database
            template = loader.get_template("reserves/forms/form_submit.html")

            return HttpResponse(template.render(context, request))
        
        else:
            listNew = None
            for _, errors in form.errors.items(): # Collects the validation errors raised and places them in a list
                listNew = list(errors)
            logger.warning("User submission failed due to: {}".format(listNew))
            # Reloads the form page, now placing the first error encountered at the top of the page
            return loadForm(request, listNew[0])

    else:
        logger.warning("User submission failed due to improper HTTP request.")
        
        return loadForm(request, "Incorrect HTTP Request sent. Try again.")
            


    