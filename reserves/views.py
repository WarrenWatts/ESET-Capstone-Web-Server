



# TODO: If time allows near the end of the Capstone project, convert this into a Class-view based format.

# Imports for Emails
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage

# Imports for REST API
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from .serializer import AccessSerializer, RsvNameSerializer
from django.http.response import JsonResponse
from rest_framework.exceptions import ParseError

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
FORM_SUBMIT_TEMPLATE = "reserves/forms/form_submit.html"
FORM_TEMPLATE = "reserves/forms/form.html"
EMAIL_TEMPLATE = "forms/email.html"

STATUS_ZERO = 0
STATUS_ONE = 1
STATUS_TWO = 2


MERIDIEM = {
    "Ante" : "A.M.",
    "Post" : "P.M.",
}

RESPONSE_MSGS = {
    1 : "Successful Entry!",
    2 : "Failed Entry!",
    3 : "Imroper JSON Formatting!",
    4 : "Invalid URL!",
    5 : "Invalid HTTP Request!",
    6 : "Invalid Data!",
    7 : "No Reservation!",
}



# Logging setup for views.py file
mainDir = Path.cwd()
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - [Line: %(lineno)d] - %(message)s')
fileHandler = RotatingFileHandler(mainDir.joinpath('reserves/logs/views.log'))
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)




# Function to display human readable times in the email
# NOTE: Only worrying about times between 6:00am through 11:00pm
def readableTime(timeVal):
    timeDate = datetime.datetime.fromtimestamp(timeVal)
    thirtyStr = "30"
    dblZeroStr = "00"

    displayHour = timeDate.hour - 12 if (timeDate.hour > 12) else timeDate.hour

    displayMinutes = thirtyStr if (timeDate.minute == 30) else dblZeroStr

    displayMeridiem = MERIDIEM["Post"] if (timeDate.hour >= 12) else MERIDIEM["Ante"]
    
    return ("{}:{} {}".format(displayHour, displayMinutes, displayMeridiem))




# Function used to validate that the current time is in the time range of a reservation 
def validateTimeRange(start, end):
    currentTimestamp = datetime.datetime.now().timestamp()

    return True if (currentTimestamp >= start and currentTimestamp < end) else False




def responseMsgHndlr(statusCode, msg):
    responseMsgVal = {"Response" : msg}

    match statusCode:
        case 0:
            logger.info(msg)

        case 1:
            logger.warning(msg)

        case 2:
            logger.critical(msg)
        
        case _:
            logger.critical("Something is very Wrong!")
            responseMsgVal = {"Response" : "Something is very Wrong!"}

    return responseMsgVal



@csrf_exempt
def httpReqHndlrAPI(request, id):
    jsonResponseVal = None

    try:
        reservesData = JSONParser().parse(request)
    except ParseError:
        return JsonResponse(data = responseMsgHndlr(STATUS_TWO, RESPONSE_MSGS[3]))

    if request.method == "POST":
        match id:
            case "value":
                jsonResponseVal = accessCheckAPI(reservesData)

            case "reserve":
                jsonResponseVal = reservationNameAPI(reservesData)
            
            case "time":
                jsonResponseVal = JsonResponse(data = responseMsgHndlr(
                                                        STATUS_ZERO, int(datetime.datetime.now().timestamp()) ))

            case _: # Shouldn't actually be able to get here since URLs are handled in urls.py
                jsonResponseVal = JsonResponse(data = responseMsgHndlr(STATUS_TWO, RESPONSE_MSGS[4]))
    else:
        jsonResponseVal = JsonResponse(data = responseMsgHndlr(STATUS_TWO, RESPONSE_MSGS[5]))
    
    return jsonResponseVal




def reservationNameAPI(reservesData):
    rsvNameSerialized = RsvNameSerializer(data = reservesData)

    responseVal = None

    if rsvNameSerialized.is_valid():
        currentRsvInfo = (Reserves.objects.filter(unixStartTime__lte = rsvNameSerialized.data["unixStartTime"])
                        .filter(unixEndTime__gt = rsvNameSerialized.data["unixStartTime"])
                        .values_list("firstName", "lastName", "unixStartTime", "unixEndTime", named = True))
        
        if currentRsvInfo:
            responseDict = {
                "firstName" : currentRsvInfo[0].firstName,
                "lastName" : currentRsvInfo[0].lastName,
                "unixStartTime" : currentRsvInfo[0].unixStartTime,
                "unixEndTime" : currentRsvInfo[0].unixEndTime,
            }

            responseVal = JsonResponse(data = responseMsgHndlr(STATUS_ZERO, responseDict))

        else:
            responseVal = JsonResponse(data = responseMsgHndlr(STATUS_ZERO, RESPONSE_MSGS[7]))

    else:
        responseVal = JsonResponse(data = responseMsgHndlr(STATUS_TWO, RESPONSE_MSGS[6]))
    
    return responseVal




# REST API that is used to check the validity of access code
def accessCheckAPI(reservesData):
    accessSerialized = AccessSerializer(data = reservesData)

    responseVal = None
    
    if accessSerialized.is_valid():
        codeTimes = (Reserves.objects.filter(accessCode = accessSerialized.data["accessCode"])
                        .values_list("unixStartTime", "unixEndTime", named = True))
        
        try:
            # NOTE: If you have time, you might consider logging a "critical" when a number of failures have occurred followed by a success
            if (validateTimeRange(codeTimes[0].unixStartTime, codeTimes[0].unixEndTime)):
                responseVal = JsonResponse(data = responseMsgHndlr(STATUS_ZERO, RESPONSE_MSGS[1]))

        except IndexError:
            responseVal = JsonResponse(data = responseMsgHndlr(STATUS_ONE, RESPONSE_MSGS[2]))
    else:
        responseVal = JsonResponse(data = responseMsgHndlr(STATUS_TWO, RESPONSE_MSGS[6]))

    return responseVal




# View for Form Page
def loadForm(request, msgString = ""):
    dateDict = dict()
    numDays = 7 # Number of calendar dates to search

    today = datetime.datetime.now()

    # If it's after the current day's last possible start time, set the first date to the next day
    baseDate = (today.date() + datetime.timedelta(1) if (today.hour >= 22 and today.minute > 30) 
                else today.date())
    
    for x in range(numDays):
        available = AvailabileTime(baseDate + datetime.timedelta(days = x), today)
        dateDict.update({available.getDate() : available.getDict()})
    
    context = {
        'myMembers' : dateDict,
        'myMessage' : msgString,
    }

    template = loader.get_template(FORM_TEMPLATE)
    return HttpResponse(template.render(context, request))



# View to check Form Page Submissions
# NOTE: Emails are not asynchronous, if time in the future, add this feature!
def checkSubmit(request):
    accessGenerator = SystemRandom()

    if request.method == "POST":
        updatedRequest = request.POST.copy()
        updatedRequest.update(uniqueAccessCode(updatedRequest))

        form = ReservesForm(updatedRequest)
        
        if form.is_valid():
            form.save()

            emailHndlr(form)
            template = loader.get_template(FORM_SUBMIT_TEMPLATE)

            return HttpResponse(template.render({}, request))
        
        else:
            listNew = None

            for _, errors in form.errors.items():
                listNew = list(errors)
            logger.warning("User submission failed due to: {}".format(listNew))

            try:
                return loadForm(request, listNew[0])
            except TypeError:
                logger.critical("Program was unable to generate an access code.")
                return loadForm(request, listNew.append("An error occurred, please try again."))

    else:
        logger.warning("User submission failed due to improper HTTP request.")
        return loadForm(request, "Incorrect HTTP Request sent. Try again.")
            


def emailHndlr(formData):
    context = {
        "firstName": formData.cleaned_data['firstName'],
        "accessCode": formData.cleaned_data['accessCode'],
        "unixStartTime": readableTime(formData.cleaned_data['unixStartTime']),
        "unixEndTime": readableTime(formData.cleaned_data['unixEndTime']),
        "date": formData.cleaned_data['date'],
    }

    # Making the email.html file into a string and stripping it of the HTML tags
    htmlMsg = render_to_string(EMAIL_TEMPLATE, context = context)
    plainMsg = strip_tags(htmlMsg)

    # Contents of the email
    message = EmailMultiAlternatives(
        subject = "Your Access Code",
        body = plainMsg,
        from_email = None,
        to = [formData.cleaned_data['email']],
    )

    message.attach_alternative(htmlMsg, "text/html")

    # Opening the Lock_Wizards_png.png image and reading it as binary
    with open(Path.joinpath(mainDir, IMG_FILE_PATH), 'rb') as imageFile:
        img = MIMEImage(imageFile.read())
        img.add_header("Content-ID", "<{}>".format(EMAIL_PNG)) # Gives the image its CID
        img.add_header("Content-Disposition", "inline", filename = EMAIL_PNG) # How the image should be displayed in the body
    
    message.attach(img)
    message.send()



def uniqueAccessCode(updatedRequest):
    accessGenerator = SystemRandom() # Used to generate an access code securely

    while(True): # This could be problematic if it breaks, so either think of a better way or test thoroughly!!!
        newAccessCode = accessGenerator.randint(1000000, 9999999)
        
        codeFilter = (Reserves.objects.filter(accessCode = newAccessCode)
                        .filter(date = updatedRequest["date"])
                        .values_list("accessCode", named = True))
        
        if not codeFilter:
            return {"accessCode": newAccessCode}
