from .models import Reserves
from pathlib import Path
import datetime, time
import logging

mainDir = Path.cwd()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - [Line: %(lineno)d] - %(message)s')
file_handler = logging.FileHandler(mainDir.joinpath('reserves/reservesLogFolder/available.log'))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)



class AvailabileTime():
    def __init__(self, newDatetime :datetime.datetime, now :datetime.datetime) -> None:
        self.date = newDatetime # The passed calendar in datetime value
        self.thirtyMin = 1800 # Thirty minutes in seconds (for Unix Time)
        self.today = now # The current datetime value
        self.timeDict = dict() # The dictionary that will be the value for each key in dateDict    
        self.__setupFunction() # Function that handles the function calls to complete the timeDict

    def __setupFunction(self):
        logger.debug("Entering __setupFunction...")
        startHour = 6 # The default hour used to create the origTimeList (hours between 0-23)
        startCount = 0 # Since available times are in increments of 30 min, used to start at 30 min for the hour if needed

        # If the calendar day is the current day and the current hour of today is greater than the default
        if self.today.date() == self.date and self.today.hour >= 6:

             # If the current minutes for the current hour is greater than 30, increase starting hour by 1
            startHour = (self.today.hour + 1 if (self.today.minute > 30)
                            else self.today.hour)

            # If the current minutes for the current hour is greater than 30, the startCount is equivalent to two times the startHour minus 12 (--> 2 times default hour)
            startCount = (startHour * 2 - 12 if (self.today.minute > 30) 
                                else startHour * 2 - 11)

        origTimeList = self.__originalTimes(startHour, startCount)

        # Remove last item from startTimes list argument and first item from endTimes list argument (11:00pm never a start time, 6:00am never an end time)
        postDbTimesList = self.__postDbTimes(origTimeList[:-1], origTimeList[1:])
        self.timeDict = self.__createDict(postDbTimesList[0], postDbTimesList[1])
        self.__logOfDict()
    

    # Creates a list of all thirty minute increment times from either the current time or 6:00am to 11:00pm
    def __originalTimes(self, hourT, startCount):
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
                                            minutesT
                                        )
            
            # Take the datetime value, change it to unix time, and append to the list.
            origTimeList.append(int(time.mktime(toUnixTime.timetuple())))
            
            # If minutesT is 30, then the next loop will be for the next hour
            hourT = hourT+1 if (minutesT == 30) else hourT

        return origTimeList
    

    def __postDbTimes(self, startTimes = None, endTimes = None):
        logger.debug("Entering __postDbTimes...")
        # MySQL database query that only looks for the current date, and only takes in the start and end times for each row
        myData = (Reserves.objects
                  .filter(date=self.date)
                  .filter(unixStartTime__gte=int(datetime.datetime.now().timestamp()))
                  .values_list('unixStartTime', 'unixEndTime', named=True)
                ) # Uses a named tuple

        if myData: # Statement checks if anything was queried 
            for queryset in myData:
                if queryset.unixStartTime in startTimes: # If queried start time in startTimes list, remove it
                    startTimes.remove(queryset.unixStartTime)
                else:
                    logger.error("Non-existent start time given.")
                
                if queryset.unixEndTime in endTimes: # If queried end time in endTimes list, remove it
                    endTimes.remove(queryset.unixEndTime)
                else:
                    logger.error("Non-existent end time given.")

                # for loop starts 30 minutes after start time, increments by 30, doesn't execute if start and stop are equal
                for i in range(queryset.unixStartTime + self.thirtyMin, 
                                queryset.unixEndTime, 
                                self.thirtyMin
                            ):
                    if i in startTimes:
                        startTimes.remove(i)
                    if i in endTimes:
                        endTimes.remove(i)

        return [startTimes, endTimes] # Return nested lists

    # Returns the finalized dictionary
    def __createDict(self, startTimes = None, endTimes = None):
        logger.debug("Entering __createDict...")
        unixTimes = {x : list() for x in startTimes} # Creates a dictionary with start times as keys and empty lists as values
        # Increment through each key in the list
        for key in unixTimes:
            incrementTime = key
            for i in range(4): # Can only be up to four possible end times per start time
                incrementTime += self.thirtyMin
                
                # Break from loop to stop appending to list if incrementTime not found in endTime list
                if incrementTime not in endTimes:
                    if i == 0:
                        logger.error("Start time did not have at least one end time.")
                    break
                
                # Append incrementTime to the key's list of end times
                unixTimes[key].append(incrementTime)
        
        return unixTimes
    
    def __logOfDict(self):
        logger.debug("Entering __logOfDict...")
        logger.info(self.getDate())

        for key, value in self.timeDict.items():
            listForLog = list()
            keyTime = datetime.datetime.fromtimestamp(key)
            for i in value:
                listValue = datetime.datetime.fromtimestamp(i)
                listForLog.append("{}:{}".format(listValue.hour, listValue.minute))
            
            logger.info("{}:{} - {}".format(keyTime.hour, keyTime.minute, listForLog))
            

    # Get calendar date of instance and return it as a string
    def getDate(self):
        logger.debug("Getting calendar date...")
        return str(self.date)
   
    # Get the timeDict for the instance
    def getDict(self):
        logger.debug("Getting time dictionary...")
        return self.timeDict