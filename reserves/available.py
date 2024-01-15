from logging.handlers import RotatingFileHandler
from .models import Reserves
from pathlib import Path
import datetime, time
import logging


# Logging setup for available.py file
mainDir = Path.cwd()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - [Line: %(lineno)d] - %(message)s')
file_handler = RotatingFileHandler(mainDir.joinpath('reserves/reservesLogFolder/available.log'))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Constants
THIRTY_MIN = 1800 # Thirty minutes in seconds (for Unix Time)

class AvailabileTime():
    def __init__(self, newDatetime :datetime.datetime, now :datetime.datetime) -> None:
        self.date = newDatetime # The passed calendar in datetime value
        self.today = now # The current datetime value
        self.timeDict = dict() # The dictionary that will be the value for each key in dateDict    
        self.__setupFunction() # Function that handles the function calls to complete the timeDict


    def __setupFunction(self) -> None:
        logger.debug("Entering __setupFunction...")
        startHour = 6 # The default hour used to create the origTimeList (hours between 0-23)
        startCount = 0 # Since available times are in increments of 30 min, used to start at 30 min for the hour if needed

        origTimeList = self.__originalTimes(startHour, startCount)

        # Remove last item from startTimes list argument and first item from endTimes list argument (11:00pm never a start time, 6:00am never an end time)
        postDbTimesList = self.__postDbTimes(origTimeList[:-1], origTimeList[1:])
        self.timeDict = self.__createDict(postDbTimesList[0], postDbTimesList[1])
        self.__logOfDict()
    

    # Creates a list of all thirty minute increment times from either the current time or 6:00am to 11:00pm
    def __originalTimes(self, hourT, startCount) -> list:
        logger.debug("Entering __originalTimes...")
        origTimeList = list() # The time list that will be returned

        # The start count starts at zero, but technically goes from 12 to 46 (double the hours for 30 min increments)...
        for j in range(startCount, 35): #...Subtracting 12 from 46 gives 34, but 1 more must be added due to range()'s functionality
            minutesT = 0 # The default for minutes (resets every loop) 

            if j % 2 == 1: # If the current count value is odd, then change minutesT to 30
                minutesT = 30
            
            toUnixTime = datetime.datetime(
                                        self.date.year,
                                        self.date.month,
                                        self.date.day,
                                        hourT,
                                        minutesT,
                                    )
            
            # Take the datetime value, change it to unix time, and append to the list.
            origTimeList.append(int(time.mktime(toUnixTime.timetuple())))
            
            # If minutesT is 30, then the next loop will be for the next hour
            hourT = hourT+1 if (minutesT == 30) else hourT

        return origTimeList
    

    def __postDbTimes(self, startTimes = None, endTimes = None) -> list:
        logger.debug("Entering __postDbTimes...")
        # MySQL database query that only looks for the current date, and only takes in the start and end times for each row
        # NOTE: Implementation here isn't of the best quality, but unless more time is acquired near the end of the project, well...it works
        myData = (
                Reserves.objects.
                filter(date=self.date).
                values_list('unixStartTime', 'unixEndTime', named=True)
            ) # Uses a named tuple
        
        # If no data, it won't loop through
        for queryset in myData: # Using .remove() in this for loop is okay since .remove() isn't for the same list being looped
            try:
                if queryset.unixStartTime % 9 != 0: # If the start time in the database is not a 30 minute increment
                    raise Exception
                if queryset.unixEndTime % 9 != 0: # If the end time in the database is not a 30 minute increment
                    raise Exception
            except:
                logger.critical("Someone has likely gained unauthorized access to the database. Incorrect time found.")
            
            if queryset.unixStartTime in startTimes: # If queried start time in startTimes list, remove it
                startTimes.remove(queryset.unixStartTime)
                endTimes.remove(queryset.unixEndTime) # Since we know that the startTime is 

                # for loop starts 30 minutes after start time, increments by 30, doesn't execute if start and stop are equal
                for i in range(
                            queryset.unixStartTime + THIRTY_MIN, 
                            queryset.unixEndTime, 
                            THIRTY_MIN,
                        ):
                    startTimes.remove(i)
                    endTimes.remove(i)
        
        if self.today.date() == self.date:
            # Re-assign startTimes to a new list only for current day (based on current time with 15 minute window).
            startTimes = [time for time in startTimes 
                            if time > int(datetime.datetime.now().timestamp()) - 900]
                
        logger.debug("Start Times List: {}".format(startTimes))
        logger.debug("End Times List: {}".format(endTimes))
        return [startTimes, endTimes] # Return nested lists


    # Returns the finalized dictionary
    def __createDict(self, startTimes = None, endTimes = None) -> dict:
        logger.debug("Entering __createDict...")
        unixTimes = {x : list() for x in startTimes} # Creates a dictionary with start times as keys and empty lists as values
        # Increment through each key in the list
        for key in unixTimes:
            incrementTime = key
            for i in range(4): # Can only be up to four possible end times per start time
                incrementTime += THIRTY_MIN
                
                # Break from loop to stop appending to list if incrementTime not found in endTime list
                if incrementTime not in endTimes:
                    if i == 0:
                        logger.error("Start time did not have at least one end time.")
                    break
                
                # Append incrementTime to the key's list of end times
                unixTimes[key].append(incrementTime)

        return unixTimes
    

    def __logOfDict(self) -> None:
        logger.debug("Entering __logOfDict...")
        logger.info(self.getDate())

        # Nested for loop that takes each key (start) time and its end times, and produces a human readable time for logging
        for key, value in self.timeDict.items():
            listForLog = list()
            keyTime = datetime.datetime.fromtimestamp(key)
            for i in value:
                listValue = datetime.datetime.fromtimestamp(i)
            # TODO: Fix flawed logic here if time (just for logging, so not of the utmost importance...)
                listForLog.append("{}:{}".format(
                                                listValue.hour, 
                                                30 if (listValue.minute == 30) else "00",
                                            )) # Statement to prevent minutes only showing a single zero
            
            logger.info("{}:{} - {}".format(
                                        keyTime.hour, 
                                        30 if (keyTime.minute == 30) else "00", 
                                        listForLog,
                                    ))
            

    # Get calendar date of instance and return it as a string
    def getDate(self) -> str:
        logger.debug("Getting calendar date...")
        return str(self.date)
    

    # Get the timeDict for the instance
    def getDict(self) -> dict:
        logger.debug("Getting time dictionary...")
        return self.timeDict