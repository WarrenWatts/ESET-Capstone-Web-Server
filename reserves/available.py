"""/* Texas A&M University
** Electronic Systems Engineering Technology
** ESET-420 Engineering Technology Capstone II
** Author: Warren Watts
** File: available.py
** --------
** Python code ............
*/"""



# Imports
from logging.handlers import RotatingFileHandler
from .models import Reserves
from pathlib import Path
import datetime, time
import logging



"""/* Variable Naming Abbreviations Legend:
**
** dir - directory
** dict - dictionary
** orig - original
** db - database
** dbl - double
** mod - modulus
** num - number
** T - time (used as a post-fix when it aids in distinguishing variables
** that are similar to keywords or other variables).
*/"""



"""/* Function Prefixes Legend:
**
** gen - generate
*/"""



"""/* Notes:
** Below is the logging setup for this file (available.py). Each log produced
** will give the date and time information, logging level value, the line number
** at which the log occurred, and the log's associated message.
*/"""
mainDir = Path.cwd()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - [Line: %(lineno)d] - %(message)s')
file_handler = RotatingFileHandler(mainDir.joinpath('reserves/logs/available.log'))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)



# Constants
THIRTY_MIN_MILLI = 1800 # Thirty minutes in seconds (for Unix Time)



"""/* Description:
** The AvailableTime() class is the backbone of much of the important information
** needed for the Form Page of the website. Given a specified datetime and the current
** datetime, this class can determine what times are available to reserve a room for a
** specified date by generating and comparing/filtering unix timestamps.
**
** Parameters:
** newDatetime - the datetime of some specified date
** now - the current datetime 
**
** Notes:
** The reason unix timestamps are used is due to their ability to be easily compared, manipulated,
** and processed by both Python and JavaScript.
** The constructor (__init__) for this class initializes the parameters in addition to creating
** a timeDict dictionary which will hold the start times and a list of their associated end times
** for each date passed to the class. In this way the information can be easily processed via JSON
** formatting when passed to the JavaScript code.
** The __setupFunction() is also called within the constructor in order to generate and filter the
** relevant data that can then be acquired through the class's get methods.
** One final note is that functions that are "privated" have two underscores placed in front of them.
*/"""
class AvailabileTime():
    def __init__(self, newDatetime :datetime.datetime, now :datetime.datetime) -> None:
        self.selectedDate = newDatetime # The passed calendar in datetime value
        self.today = now # The current datetime value
        self.timeDict = dict() # The dictionary that will be the value for each key in dateDict    
        self.__setupFunction() # Function that handles the function calls to complete the timeDict



    """/* Description:
    ** The __setupFunction() function is a function that contains the callers of other
    ** functions in this class. These callers are for the functions that generate and
    ** filter data necessary to be obtained by other Python modules.
    */"""
    def __setupFunction(self) -> None:
        logger.debug("Entering __setupFunction...")
        # The default starting hour used to create the origTimeList (hours between 0-23)
        startHour = 6

        # The default hour at which to begin counting in 30 min. increments
        startCount = 0

        origTimeList = self.__genOrigTimes(startHour, startCount)

        """/* Notes:
        ** The list slicing in the function arguments below removes the last item from startTimes list 
        ** and first item from endTimes list. The reason for this is because 11:00pm will never be a 
        ** start time and 6:00am will never be an end time.
        ** It should also be noted that the __filterDbTimes function returns a list of lists, which
        ** is why the arguments in __genDict() are indexed.
        */"""
        postDbTimesList = self.__filterDbTimes(origTimeList[:-1], origTimeList[1:])
        self.timeDict = self.__genDict(postDbTimesList[0], postDbTimesList[1])
        self.__genLogOfDict()
    


    """/* Description:
    ** The __genOrigTimes() function produces a list of all 30 min. increment times from between
    ** 6:00am to 11:00pm for some date. They are initially in the datetime type format, however, 
    ** they are then converted into unix timestamps.
    **
    ** Parameters:
    ** hourT - the hour at which to start the counting
    ** startCount - the initial value (in thirty minute increments) by which to start counting
    **
    ** Return:
    ** A list of unix timestamps between 6:00am to 11:00pm for a given date is returned.
    */"""
    def __genOrigTimes(self, hourT, startCount) -> list:
        logger.debug("Entering __genOrigTimes...")

        # The time list that will be returned
        origTimeList = list()

        thirtyMin = 30
        modNum = 2

        """/* Notes:
        ** The start count starts at zero, but technically goes from 12 to 46 (double the hours for 30 min increments).
        ** Subtracting 12 from 46 gives 34, i.e., the value we must count through to produce a timestamp
        ** for every time from 6:00am to 11:00pm. A value of 1 must be added, however, due to range()'s functionality.
        */"""
        endCount = 35

        for j in range(startCount, endCount):

            # The default for minutes (resets every loop) 
            minutesT = 0

            # Changes to 30 minutes when the current count is odd
            if j % modNum == 1:
                minutesT = thirtyMin
            

            toUnixTime = datetime.datetime(
                            self.selectedDate.year,
                            self.selectedDate.month,
                            self.selectedDate.day,
                            hourT,
                            minutesT,
                        )
            
            # Take the datetime value, change it to unix time, and append to the list.
            origTimeList.append(int(time.mktime(toUnixTime.timetuple())))
            
            # If minutesT is 30, then the next loop will be for the next hour
            hourT = hourT + 1 if (minutesT == thirtyMin) else hourT

        return origTimeList
    


    """/* Description:
    ** The __filterDbTimes() function is used to determine which start times and which end times are available
    ** by comparing the start and end unix timestamp values stored in the data base. The logic for this is thus...
    ** If a unix start timestamp is taken, that does not mean that it has also been taken as a unix end timestamp.
    ** So, the unix start timestamp is only removed from the startTimes list. This idea can also be applied to the 
    ** unix end timestamp for endTimes list. For the timestamps that  occur between a database entry's unix start 
    ** timestamp and unix end timestamp, they must be removed from both the startTimes and endTimes list. If the
    ** selectedDate parameter for the class is the current day, then the startTimes list will be purged of all times
    ** less than the current time plus an additional fifteen minute window.
    **
    ** Parameters:
    ** startTimes - a list of all the original possible unix timestamp start times
    ** endTimes a list of all the original possible unix timestamp end times
    **
    ** Return:
    ** A list of lists is returned, the first list containing all possible start times
    ** for a given date, and the second list containing all the possible end times for a given date.
    **
    ** Notes:
    **The reasoning for only manipulating the startTimes list here and not the endTimes will be understood 
    ** once done reading on the __genDict() function.
    */"""
    def __filterDbTimes(self, startTimes = None, endTimes = None) -> list:
        logger.debug("Entering __filterDbTimes...")

        """/* Notes:
        ** This is a MySQL database query that only looks for the selected date, and only takes
        ** in the unix start timestamps and end timestamps for each of these entries. These
        ** entries are stored in a named tuple.
        */"""
        myDbData = (
                Reserves.objects.
                filter(date=self.selectedDate).
                values_list("unixStartTime", "unixEndTime", named=True)
            )
        
        """/* Notes:
        ** It may be obvious but just to state it, if no data is found from the MySQL query
        ** then this for loop will be ignored.
        ** Also not that in the case of this for loop, it is okay to use the .remove() method
        ** since we are not looping through the list that we are currently removing items from!
        */"""
        for queryset in myDbData:

            """/* Notes:
            ** Here we are checking to make sure that all the unix timestamp entries queried from the
            ** database are actually in thirty minute increments. If they are not, then either someone
            ** managed to bypass both client and server-side validations (extremely unlikely due to the
            ** way in which unix timestamps are validated on the server-side) or someone is directly
            ** inputting rows into the database incorrectly (whether they are an "inside" threat actor
            ** or not).
            */"""
            try:
                if queryset.unixStartTime % THIRTY_MIN_MILLI != 0:
                    raise Exception
                if queryset.unixEndTime % THIRTY_MIN_MILLI != 0:
                    raise Exception
            except:
                logger.critical("Someone has likely gained unauthorized access to the database. Incorrect time found.")
            
            """/* Notes:
            ** If a start time from a database entry finds a match in the startTimes list
            ** then we can be certain that the entry's end time will also find a match in 
            ** the endTime list (bar the error stated above).
            */"""
            if queryset.unixStartTime in startTimes:
                startTimes.remove(queryset.unixStartTime)
                endTimes.remove(queryset.unixEndTime)

                """/* Notes:
                ** The for loop starts 30 minutes after start time, increments by 30, 
                ** and doesn't execute if the start and stop values are equal.
                */"""
                for i in range(queryset.unixStartTime + THIRTY_MIN_MILLI, 
                                queryset.unixEndTime, 
                                THIRTY_MIN_MILLI):
                    startTimes.remove(i)
                    endTimes.remove(i)
        
        if self.today.date() == self.selectedDate:
            startTimes = [time for time in startTimes 
                            if time > int(datetime.datetime.now().timestamp()) - 900]
                
        logger.debug("Start Times List: {}".format(startTimes))
        logger.debug("End Times List: {}".format(endTimes))
        return [startTimes, endTimes]



    """/* Description:
    ** The __genDict() function generates a dictionary where the available unix start timestamps are used as the keys
    ** the value pair is made up of the available unix end timestamps for the start time. Each start time will check
    ** if up to four thirty minute increment times (e.g. if I start at 6:00am then 6:30am, 7:00am, 7:30am, and 8:00am)
    ** are available by cross checking to see if these increments are inside the endTimes list. If they aren't, one is
    ** not, then extent of possible end times has been found for a given start time. At the very least, each available start
    ** time should have one end time. With this logic, it becomes understandable as to why the values of the startTimes list
    ** were only changed in the case where it was the current day. If the start time isn't even available, then even if the
    ** end timestamp is still within the endTimes list, it will not be checked.
    **
    ** Parameters:
    ** startTimes - a list of all the currently available unix timestamp start times
    ** endTimes a list of all the currently available (plus some) unix timestamp end times
    **
    ** Return:
    ** A dictionary containing the unix start timestamps as keys and their corresponding unix end timestamp 
    ** list as values is returned.
    **
    ** Notes:
    ** There are four layers of nesting here, however, this only occurs in order to enable the logging of a
    ** potentially critical error.
    */"""
    # Returns the finalized dictionary
    def __genDict(self, startTimes = None, endTimes = None) -> dict:
        logger.debug("Entering __genDict...")

        incrementsOfThirty = 4

        unixTimesDict = {x : list() for x in startTimes}

        for startT in unixTimesDict:
            incrementTime = startT

            for i in range(incrementsOfThirty):
                incrementTime += THIRTY_MIN_MILLI
                
                if incrementTime not in endTimes:
                    if i == 0:
                        logger.error("Start time did not have at least one end time.")
                    break
                
                # Append incrementTime to the key's list of end times
                unixTimesDict[startT].append(incrementTime)

        return unixTimesDict
    


    """/* Description:
    ** The __genLogOfDict() function takes the final generated dictionary from __genDict()
    ** and translates each key (unix start timestamp) and their associated values (list of
    ** unix end timestamps) and translates them into human readable times for logging/debugging
    ** purposes. The date corresponding to this dictionary is also logged just before the creation
    ** of the dictionary's details.
    **
    ** Notes:
    ** Although nothing is returned in the general sense, a log of the dictionary is created.
    */"""
    def __genLogOfDict(self) -> None:
        logger.debug("Entering __genLogOfDict...")
        logger.info(self.getDate())

        # String used since 00 is a not a producable int value from the .minute method
        thirtyStr = "30"
        dblZeroStr = "00"

        for startTimeKey, endTimes in self.timeDict.items():
            keyTime = datetime.datetime.fromtimestamp(startTimeKey)
            logsList = list()

            startMinutes = thirtyStr if (keyTime.minute == 30) else dblZeroStr

            for i in endTimes:
                endTimeVal = datetime.datetime.fromtimestamp(i)

                endMinutes = thirtyStr if (endTimeVal.minute == 30) else dblZeroStr

                logsList.append("{}:{}".format(endTimeVal.hour, endMinutes))
            
        
            logger.info("{}:{} - {}".format(keyTime.hour, startMinutes, logsList))
            


    """/* Description:
    ** This function simply returns an ISO formatted string of the date
    ** of the object.
    **
    ** Return:
    ** An ISO formatted string of the object's date is returned.
    */"""
    # Get calendar date of instance and return it as a string
    def getDate(self) -> str:
        logger.debug("Getting calendar date...")
        return str(self.selectedDate)



    """/* Description:
    ** This function simply returns the dictionary generated
    ** by the __genDict() function.
    **
    **
    ** Return:
    ** A dictionary of the start timestamps and corresponding end timestamps
    ** is returned.
    */"""
    # Get the timeDict for the instance
    def getDict(self) -> dict:
        logger.debug("Getting time dictionary...")
        return self.timeDict