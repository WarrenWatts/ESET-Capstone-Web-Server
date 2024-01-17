# Imports for Emails
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage

# Imports for REST API
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from .serializer import ReservesSerializer
from django.http.response import JsonResponse

# Imports for General Django
from .available import AvailabileTime
from django.http import HttpResponse
from django.template import loader
from .forms import ReservesForm
from .models import Reserves

# Other Imports
from logging.handlers import RotatingFileHandler
from secrets import SystemRandom
from pathlib import Path
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
# NOTE: Only worrying about times between 6:00am through 11:00pm
def readableTime(timeVal):
    timeDate = datetime.datetime.fromtimestamp(timeVal)

    displayHour = timeDate.hour - 12 if (timeDate.hour > 12) else timeDate.hour
    
    return ("{}:{} {}".format(
                                displayHour, 
                                "30" if (timeDate.minute == 30) else "00", 
                                "P.M." if (timeDate.hour >= 12) else "A.M.",
                            ))


# Function used to validate that the current time is in the time range of a reservation 
def validateTimeRange(start, end):
    currentTimestamp = datetime.datetime.now().timestamp()

    return True if (currentTimestamp >= start and currentTimestamp < end) else False
        


# REST API that is used to check the validity of access code
@csrf_exempt
def reservesAPI(request):
    if request.method == "POST": # Fails if not a post request
        reserves_data = JSONParser().parse(request) # Parses request from JSON into usable
        reserves_serializer = ReservesSerializer(data=reserves_data) # Serialize 
        if reserves_serializer.is_valid():
            
            # This should only give back one object, but it may be best for us to verify that the...
            # ...access code generated hasn't already been generated before and placed in the database.
            codeTimes = (Reserves.objects.filter(accessCode=reserves_serializer.data["accessCode"])
                            .values_list('unixStartTime', 'unixEndTime', named=True))
            
            # NOTE: If logging, may want to add a logging statement to the failures if possible
            return (JsonResponse({"response":"Success"}) 
                        if (validateTimeRange(codeTimes[0].unixStartTime, codeTimes[0].unixEndTime)) 
                            else JsonResponse({"response":"Failure"}))
        else: # TODO: Add logger
            return JsonResponse(data={"response":"Invalid Data"})
    
    else: # TODO: Add logger
        return JsonResponse({"response":"Wrong HTTP Request"})



# View for Home/Main Page
def mainPage(request):
    template = loader.get_template("reserves/index.html")
    return HttpResponse(template.render(dict(), request))



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

    if request.method == "POST": # Only execute code if the HTTP request is POST
        updated_request = request.POST.copy()
        updated_request.update({"accessCode": accessGenerator.randint(1000000, 9999999)})
        form = ReservesForm(updated_request) # Update POST request with new accessCode field
        
        if form.is_valid(): # Causes the form fields sent to be validated. Invalid if any errors found
            form.save() # Saves form info to the database

            # Context dictionary to be sent to email.html file
            context = {
                "firstName": form.cleaned_data['firstName'],
                "accessCode": form.cleaned_data['accessCode'],
                "unixStartTime": readableTime(form.cleaned_data['unixStartTime']),
                "unixEndTime": readableTime(form.cleaned_data['unixEndTime']),
                "date": form.cleaned_data['date'],
            }

            # Making the email.html file into a string and stripping it of the HTML tags
            html_message = render_to_string("forms/email.html", context = context)
            plain_message = strip_tags(html_message)

            # Contents of the email
            message = EmailMultiAlternatives(
                subject = "Your Access Code",
                body = plain_message,
                from_email = None,
                to = [form.cleaned_data['email']],
            )

            # Attaching an alternative version of the html
            message.attach_alternative(html_message, "text/html")

            # Opening the Lock_Wizards_png.png image and reading it as binary
            with open(Path.joinpath(mainDir, IMG_FILE_PATH), 'rb') as imageFile:
                img = MIMEImage(imageFile.read())
                img.add_header('Content-ID', '<{}>'.format(EMAIL_PNG)) # Gives the image its CID
                img.add_header('Content-Disposition', 'inline', filename=EMAIL_PNG) # How the image should be displayed in the body
            
            message.attach(img) # Attaching the CID image to the message that will be sent to the email
            message.send() # Sending email message

            template = loader.get_template("reserves/forms/form_submit.html")

            return HttpResponse(template.render(context, request))
        
        else:
            listNew = None
            for _, errors in form.errors.items(): # Collects the validation errors raised and places them in a list
                listNew = list(errors)
            logger.warning("User submission failed due to: {}".format(listNew))

            try: # If, for some reason, the program is unable to generate an access code, a TypeError will be encountered.
                return loadForm(request, listNew[0]) # Reloads the form page, now placing the first error encountered at the top of the page
            except TypeError:
                logger.critical("Program was unable to generate an access code.")
                return loadForm(request, listNew.append("An error occurred, please try again."))

    else:
        logger.warning("User submission failed due to improper HTTP request.")
        return loadForm(request, "Incorrect HTTP Request sent. Try again.")
            


    