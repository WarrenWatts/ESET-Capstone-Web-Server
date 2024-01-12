from django.contrib import messages
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from .available import AvailabileTime
from .forms import ReservesForm
from .models import Reserves
from secrets import SystemRandom
import datetime
import json

# Create your views here.

def mainPage(request):
    template = loader.get_template("reserves/index.html") 
    context = dict()
    return HttpResponse(template.render(context, request))



def loadForm(request, msgString=""):
    dateDict = dict() # Dictionary to hold dates and their start/end times
    numDays = 7 # Number of calendar dates to search
    today = datetime.datetime.now()
    baseDate = (today.date() + datetime.timedelta(1) if (today.hour >= 22 and today.minute > 30) 
                else today.date()) # If it's after the current day's last possible start time, set the first date to the next day
    
    for x in range(numDays): # Send each date to the AvailableTime class to fill the dateDict
        available = AvailabileTime(baseDate + datetime.timedelta(days=x), today)
        dateDict.update({available.getDate() : available.getDict()}) # The key of this dictionary is the calendar date, the value is another dictionary
    
    dateJSON = json.dumps(dateDict) # Format the dateDict into JSON
    context = {'myMembers' : dateDict} # The data given by Django to HTML must be in dictionary form
    template = loader.get_template("reserves/forms/form.html") 
    if msgString:
        messages.add_message(request, messages.ERROR, msgString)
    return HttpResponse(template.render(context, request))



def checkSubmit(request):
    accessGenerator = SystemRandom()
    codeValue = accessGenerator.randint(1000000, 9999999)
    context = {}

    if request.method == "POST":
        updated_request = request.POST.copy()
        updated_request.update({"accessCode": codeValue})
        print(updated_request)
        form = ReservesForm(updated_request)
        
        if form.is_valid():
            form.save()

            template = loader.get_template("reserves/forms/form_submit.html")
            return HttpResponse(template.render(context, request))
        else:
            for _, errors in form.errors.items():
                listNew = list(errors)
            return loadForm(request, listNew[0])

    
    else:
        pass # TODO...
            


    