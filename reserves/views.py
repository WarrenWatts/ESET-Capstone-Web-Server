from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
from django.template.loader import render_to_string
from logging.handlers import RotatingFileHandler
from django.utils.html import strip_tags
from .available import AvailabileTime
from django.http import HttpResponse
from django.template import loader
from secrets import SystemRandom
from .forms import ReservesForm
from pathlib import Path
from PIL import Image
import datetime
import logging



# Constants
EMAIL_PNG = 'Lock_Wizards_png.png'
IMG_FILE_PATH = 'reserves/templates/reserves/static/pictures/logo/Lock_Wizards_png.png'


# Logging setup for views.py file
mainDir = Path.cwd()
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - [Line: %(lineno)d] - %(message)s')
file_handler = RotatingFileHandler(mainDir.joinpath('reserves/reservesLogFolder/views.log'))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)



# Function to display human readable times in the email
def readableTime(timeVal):
    timeDate = datetime.datetime.fromtimestamp(timeVal)
    displayHour = timeDate.hour
    displayMin = timeDate.minute
    hourPeriod = "A.M."
    extraZero = ""

    if displayHour > 12:
        displayHour -= 12
        hourPeriod = "P.M."

    if displayMin <= 9:
        extraZero = "0"
    
    return ("{}:{}{} {}".format(displayHour, extraZero, displayMin, hourPeriod))



# View for Home/Main Page
def mainPage(request):
    template = loader.get_template("reserves/index.html") 
    context = dict()
    return HttpResponse(template.render(context, request))



# View for Form Page
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



# View to check Form Page Submissions
# NOTE: Emails are not asynchronous, if time in the future, add this feature!
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

            context = {
                "firstName": form.cleaned_data['firstName'],
                "accessCode": form.cleaned_data['accessCode'],
                "unixStartTime": readableTime(form.cleaned_data['unixStartTime']),
                "unixEndTime": readableTime(form.cleaned_data['unixEndTime']),
                "date": form.cleaned_data['date'],
            }

            html_message = render_to_string("forms/email.html", context = context)
            plain_message = strip_tags(html_message)

            message = EmailMultiAlternatives(
                subject = "Email Django Test",
                body = plain_message,
                from_email = None,
                to = [form.cleaned_data['email']],
            )

            message.attach_alternative(html_message, "text/html")

            with open(Path.joinpath(mainDir, IMG_FILE_PATH), 'rb') as imageFile:
                img = MIMEImage(imageFile.read())
                img.add_header('Content-ID', '<{}>'.format(EMAIL_PNG)) # Gives the image its CID
                img.add_header('Content-Disposition', 'inline', filename=EMAIL_PNG) # How the image should be displayed in the body
            
            message.attach(img)
            message.send()

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
            


    