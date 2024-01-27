"""/* Texas A&M University
** Electronic Systems Engineering Technology
** ESET-420 Engineering Technology Capstone II
** Author: Warren Watts
** File: views.py
** --------
** The views.py file holds Django views functions that take in web
** requests and return web responses. Additionally, other
** "helper" functions were added to aid these view functions.
** For more information on Django views, go to 
** https://docs.djangoproject.com/en/5.0/topics/http/views/
*/"""



# Imports for Emails
from .tasks import emailHndlr

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



"""/* Variable Naming Abbreviations Legend:
**
** min - minutes
** btm - bottom
** msg(s) - message(s)
** dbl - double
** val - value
** req - request
** rsv - reserve
** dict - dictionary
** num - number
*/"""



"""/* Function Prefixes Legend:
**
** v - view
** h - helper
** r - REST API
*/"""



# Constants
FORM_SUBMIT_TEMPLATE = "reserves/forms/form_submit.html"
FORM_TEMPLATE = "reserves/forms/form.html"

THIRTY_MIN = 30

# Status codes for logging (0 is info, 1 is warning, 2 is critical)
STATUS_ZERO = 0
STATUS_ONE = 1
STATUS_TWO = 2

MERIDIEM = {
    "Ante" : "A.M.",
    "Post" : "P.M.",
}

FORM_FIELD_NAMES = [
    "firstName", 
    "lastName", 
    "email", 
    "date", 
    "unixStartTime", 
    "unixEndTime",
]

# Reponses to REST API POST requests
RESPONSE_MSGS = {
    1 : "Successful Entry!",
    2 : "Failed Entry!",
    3 : "Imroper JSON Formatting!",
    4 : "Invalid URL!",
    5 : "Invalid HTTP Request!",
    6 : "Invalid Data!",
    7 : "No Reservation!",
}



"""/* Notes:
** Below is the logging setup for this file (views.py). Each log produced
** will give the date and time information, logging level value, the line number
** at which the log occurred, and the log's associated message.
*/"""
MAIN_DIR = Path.cwd()
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - [Line: %(lineno)d] - %(message)s")
fileHandler = RotatingFileHandler(MAIN_DIR.joinpath("reserves/logs/views.log"))
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)



"""/* Description:
** The hValidateTimeRange function is used to validate that the current time 
** is in the time range of a reservation. Used when an input access code is sent
** from the microcontroller via a POST request.
**
** Parameters:
** start - the unix start time for the reservation
** end - the unix end time for the reservation
**
** Return:
** A Boolean value of either True or False is returned depending on whether or not
** the current time is within the reservation time.
*/"""
def hValidateTimeRange(start, end):
    currentTimestamp = datetime.datetime.now().timestamp()

    return True if (currentTimestamp >= start and currentTimestamp < end) else False



"""/* Description:
** The hReadableTime() function allows unix timestamps to be 
** displayed in a human readable form for the emails.
**
** Parameters:
** timeVal - the unix timestamp value sent to the function
**
** Return:
** returns a string of the time in the format... 9:30 P.M.
**
** Notes:
** We are ONLY concerned with times between 6:00am and 11:00pm 
** in increments of 30 minutes, which is why this function works
** properly with such simplicity.
*/"""
def hReadableTime(timeVal):
    timeDate = datetime.datetime.fromtimestamp(timeVal)
    twelveHours = 12
    thirtyStr = "30"
    dblZeroStr = "00"

    displayHour = timeDate.hour - twelveHours if (timeDate.hour > twelveHours) else timeDate.hour

    displayMinutes = thirtyStr if (timeDate.minute == THIRTY_MIN) else dblZeroStr

    displayMeridiem = MERIDIEM["Post"] if (timeDate.hour >= twelveHours) else MERIDIEM["Ante"]
    
    return ("{}:{} {}".format(displayHour, displayMinutes, displayMeridiem))



"""/* Description:
** The hResponseMsgHndlr() function handles occurrences from the
** rHttpReqHndlrAPI(), hRsvNameAPI(), and hAccessCheckAPI() functions,
** logging the occurrence based on it's log level. Each occurrence/event
** has its own message which is stored in the RESPONSE_MSGS dictionary.
**
** Parameters:
** statusCode - code associated with the occurrence's logging level
** msg - message to be attached to the response
**
** Return:
** A dictionary containing the response message is returned
**
** Notes:
** A 0 means that a success event has occurred. A 1 means that a failure event has 
** occurred. A 2 means that event has occurred that may possibly point
** to a security risk/breach or major flaw in the code.
*/"""
def hResponseMsgHndlr(statusCode, msg):
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



"""/* Description:
** The hRsvNameAPI() function is the helper function used when the "/reserve/" URL is sent
** an HTTP POST request. It verifies the data matches the field's specifications (field of a model)
** with a serializer class (in this case the field is the unixStartTime). If valid, a database query is made 
** to check if the the unix timestamp sent is greater than or equal to a database entry's unixStartTime value and less than
** it's corresponding unixEndTime value. This shows whether or not a reservation exists at the current time.
**
** Parameters:
** reservesData - contains the JSON parsed POST request data
**
** Return:
** A JSON data structure is returned as the response to the HTTP request. This structure contains info on
** the first and last name of the individual who made the current reservation, as well as the start and end
** time of the current reservation. (That is, if the data is valid and a reservation is found for the current time).
**
** Notes:
** If there isn't a reservation made for the current time, a message stating as much will be returned.
*/"""
def hRsvNameAPI(reservesData):
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

            responseVal = JsonResponse(data = hResponseMsgHndlr(STATUS_ZERO, responseDict))

        # If reservation doesn't exist
        else:
            responseVal = JsonResponse(data = hResponseMsgHndlr(STATUS_ZERO, RESPONSE_MSGS[7]))

    # If data sent is invalid
    else:
        responseVal = JsonResponse(data = hResponseMsgHndlr(STATUS_TWO, RESPONSE_MSGS[6]))
    
    return responseVal



"""/* Description:
** The hAccessCheckAPI() function is the helper function used when the "/value/" URL is sent
** an HTTP POST request. It verifies the data matches the field's specifications (field of a model)
** with a serializer class (in this case the field is the accessCode). If valid, a database query is made 
** to check if the access code exists, producing entries for the current date which the access code is associated with
** (in reality it can only have one entry associated with it due to the way things have been programmed),
** more specifically producing values for entry's unixStartTime and unixEndTime. If the unixStartTime and unixEndTime 
** can fit the current unix time within their range, then the accessCode was correct.
**
** Parameters:
** reservesData - contains the JSON parsed POST request data
**
** Return:
** A JSON data structure is returned as the response to the HTTP request. This response varies based
** on the id value and the occurrence/event encountered.
*/"""
# REST API that is used to check the validity of access code
def hAccessCheckAPI(reservesData):
    accessSerialized = AccessSerializer(data = reservesData)

    responseVal = None
    
    if accessSerialized.is_valid():
        codeTimes = (Reserves.objects.filter(accessCode = accessSerialized.data["accessCode"])
                        .filter(date = accessSerialized.data["date"])
                        .values_list("unixStartTime", "unixEndTime", named = True))
        
        try:
            if (hValidateTimeRange(codeTimes[0].unixStartTime, codeTimes[0].unixEndTime)):
                responseVal = JsonResponse(data = hResponseMsgHndlr(STATUS_ZERO, RESPONSE_MSGS[1]))

            # If access code exists for date but is used at the wrong time
            else:
                raise IndexError
        
        # If access code doesn't exist
        except IndexError:
            responseVal = JsonResponse(data = hResponseMsgHndlr(STATUS_ONE, RESPONSE_MSGS[2]))
    
    # If data sent is invalid
    else:
        responseVal = JsonResponse(data = hResponseMsgHndlr(STATUS_TWO, RESPONSE_MSGS[6]))

    return responseVal



"""/* Description:
** The hUniqueAccessCode() function verifies that the access code created on a date
** is not the same as any of the other access codes that have already been produced
** for the same date. (Although it is very unlikely that this would occur in the first
** place, better safe than sorry!)
**
** Parameters:
** updatedRequest - a copy of the data from the form POST request
**
** Return:
** A dictionary containing the unique access code is returned.
**
** Notes:
** To prevent the possibility of an endless loop, a counter and a corresponding if
** statement have been added.
*/"""
def hUniqueAccessCode(updatedRequest):
    accessGenerator = SystemRandom() # Used to generate an access code securely
    btmOfRange = 1000000
    topOfRange = 9999999

    countToError = 0

    # There are only (at most) 34 possible reservation periods in a day
    errorReached = 34

    newAccessCode = 0

    while(True):
        countToError = countToError + 1
        newAccessCode = accessGenerator.randint(btmOfRange, topOfRange)
        
        codeFilter = (Reserves.objects.filter(accessCode = newAccessCode)
                        .filter(date = updatedRequest["date"])
                        .values_list("accessCode", named = True))
        
        if (not codeFilter):
            break
        
        if countToError == errorReached:
            logger.critical("Either a statistical impossibility just occurred, or your code it flawed...")

            break
    
    return {"accessCode": newAccessCode}



"""/* Description:
** The hValidateFormData() function ensures that all form input fields
** exist. If fields that should exist didn't exist upon submission, errors
** could occur.
**
** Parameters:
** updatedRequest - a copy of the data from the form POST request
**
** Return:
** A boolean variable is returned, being false if the data exists and true if it does not.
*/"""
def hValidateFormData(updatedRequest):
    failureBool = False

    for i in FORM_FIELD_NAMES:
        if i not in updatedRequest.keys():
            failureBool = True
            break
    
    return failureBool



"""/* Description:
** The rHttpReqHndlrAPI() function takes in the REST API HTTP requests. It verifies
** that the request is parsible, verifies that the request is a POST request,
** and then checks which id the POST request is associated with, passing it to its 
** associated function (if any).
**
** Parameters:
** request - information from the HTTP request
** id - the value of the url from which the HTTP request was sent (specifies how it should be handled)
**
** Return:
** A JSON data structure is returned as the response to the HTTP request. This response varies based
** on the id value and the occurrence/event encountered.
**
** Notes:
** "value" is accessed when a POST request is sent to ".../value/". The POST request is checking
** to see if the access code input on the touchscreen device actually exists and is usable at the 
** current time. "reserve" is accessed when a POST request is sent to ".../reserve/". The POST request
** is checking to see if there is a reservation at the current unix timestamp (which is the info that
** is sent). "time" is accessed when a POST request is sent to ".../time/". The POST request wants
** the server to send back the current unix timestamp so that the microcontroller can begin counting on
** its RTC.
*/"""
@csrf_exempt
def rHttpReqHndlrAPI(request, id):
    jsonResponseVal = None

    try:
        reservesData = JSONParser().parse(request)
    except ParseError:
        return JsonResponse(data = hResponseMsgHndlr(STATUS_TWO, RESPONSE_MSGS[3]))

    if request.method == "POST":
        match id:
            case "value":
                jsonResponseVal = hAccessCheckAPI(reservesData)

            case "reserve":
                jsonResponseVal = hRsvNameAPI(reservesData)
            
            case "time":
                jsonResponseVal = JsonResponse(data = hResponseMsgHndlr(
                                                        STATUS_ZERO, int(datetime.datetime.now().timestamp()) ))
            
            # If URL is incorrect (shouldn't actually be able to get here since URLs are handled in urls.py)
            case _:
                jsonResponseVal = JsonResponse(data = hResponseMsgHndlr(STATUS_TWO, RESPONSE_MSGS[4]))
    
    # If not a POST request
    else: 
        jsonResponseVal = JsonResponse(data = hResponseMsgHndlr(STATUS_TWO, RESPONSE_MSGS[5]))
    
    return jsonResponseVal



"""/* Description:
** The vLoadForm function is the view function that loads the website's form page. It uses the
** AvailableTimes() classes to generate a dictionary where the keys are the dates (starting from 
** the current date to a week from the current date) and the values are the dictionaries produced by
** the AvailableTimes() class for each date. This information is then passed along to the HTML to be
** used by the JavaScript code. It should be noted that an additional parameter (msgString) is used
** when vLoadForm is "reloaded" in the cause of a submission failing due to an error. This parameter
** provides the error message string that will be placed in the HTML for the user.
**
** Parameters:
** request - the information/data from the GET request
** msgString - the string of an error message that is sent to the HTML
**
** Return:
** An HTTP response that loads the form page of the website is returned.
*/"""
def vLoadForm(request, msgString = ""):
    dateDict = dict()
    numDays = 7 # Number of calendar days to search
    addOneDay = 1
    finalRsvHour = 22

    today = datetime.datetime.now()

    # If it's after the current day's last possible start time, set the first date to the next day
    baseDate = (today.date() + datetime.timedelta(addOneDay) if (today.hour >= finalRsvHour and today.minute > THIRTY_MIN) 
                else today.date())
    
    for x in range(numDays):
        available = AvailabileTime(baseDate + datetime.timedelta(days = x), today)
        dateDict.update({available.getDate() : available.getDict()})
    
    context = {
        "myMembers" : dateDict,
        "myMessage" : msgString,
    }

    template = loader.get_template(FORM_TEMPLATE)
    return HttpResponse(template.render(context, request))



"""/* Description:
** The vCheckSubmit function is the view function that verifies and validates the info sent from the form
** via POST request. If the info is proven to be valid, then an email with an access code is sent 
** asynchronously to the user, and the form submit webpage is loaded. Otherwise, the page is sent
** to the vLoadForm() function again with the error message text associated with the cause of the reloading
** of the form page.
**
** Parameters:
** request - the information/data from the POST request
**
** Return:
** An HTTP response that loads the form submit page of the website is returned if all the information is validated
** and verified successfully. Otherwise, the page is reloaded with an associated error message.
**
** Notes:
** Even if there are multiple errors that occur, only the first one will be displayed upon reloading the form page.
*/"""
# View to check Form Page Submissions
def vCheckSubmit(request):
    if request.method == "POST":
        updatedRequest = request.POST.copy()

        # Verify that all form input data exists
        if hValidateFormData(updatedRequest):
            return vLoadForm(request, "Data missing from form, please try again.")

        updatedRequest.update(hUniqueAccessCode(updatedRequest))
        form = ReservesForm(updatedRequest)
        
        if form.is_valid():
            form.save()

            context = {
                "firstName": form.cleaned_data["firstName"],
                "accessCode": form.cleaned_data["accessCode"],
                "unixStartTime": hReadableTime(form.cleaned_data["unixStartTime"]),
                "unixEndTime": hReadableTime(form.cleaned_data["unixEndTime"]),
                "date": form.cleaned_data["date"],
            }
            
            # Send the email asynchronously
            emailHndlr.delay(context, form.cleaned_data["email"])
            template = loader.get_template(FORM_SUBMIT_TEMPLATE)

            return HttpResponse(template.render({}, request))
        
        else:
            listOfErrors = None

            for _, errors in form.errors.items():
                listOfErrors = list(errors)
            logger.warning("User submission failed due to: {}".format(listOfErrors))

            try:
                return vLoadForm(request, listOfErrors[0])
            except TypeError:
                logger.critical("Program was unable to generate an access code.")

                return vLoadForm(request, "An error occurred, please try again.")

    else:
        logger.warning("User submission failed due to improper HTTP request.")
        
        return vLoadForm(request, "Incorrect HTTP Request sent, please try again.")
