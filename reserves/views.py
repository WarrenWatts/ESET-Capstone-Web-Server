from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from .available import AvailabileTime
import datetime, time
import json

# Create your views here.

def mainPage(request):
    template = loader.get_template("reserves/index.html") 
    
    return HttpResponse(template.render(request))

def loadForm(request):
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
    
    return HttpResponse(template.render(context, request))