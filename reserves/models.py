"""/* Texas A&M University
** Electronic Systems Engineering Technology
** ESET-420 Engineering Technology Capstone II
** Author: Warren Watts
** File: models.py
** --------
** The models.py file holds Django models. Each model contains fields that store data
** into a database. These fields can have limits set as well as 
** their own validator functions. For more information on Django models, go to 
** https://docs.djangoproject.com/en/5.0/topics/db/models/
*/"""



# Imports
from django.core.validators import RegexValidator
from django.db import models



"""/* Variable Naming Abbreviations Legend:
**
** str - string
** regex - regular expression
*/"""



# Constants
"""/* Notes:
** The message sent back to the webpage when someone deliberately attempts to edit 
** the client-side code to try and alter what is sent in the POST request upon submission.
*/"""
SUSPICIOUS_STR = "You edited the page code to try and submit something..."

NAME_REGEX = r"^[A-za-z]{1,50}$"
EMAIL_REGEX = r"^[A-Za-z\._\-0-9]*[@][A-Za-z]*[\.][a-z]{2,4}$"



# Create your models here.
class Reserves(models.Model):
    firstName = models.CharField(max_length = 11, validators = [RegexValidator(regex = NAME_REGEX, message = SUSPICIOUS_STR)])
    lastName = models.CharField(max_length = 50, validators = [RegexValidator(regex = NAME_REGEX, message = SUSPICIOUS_STR)])
    email = models.EmailField(max_length = 62, validators = [RegexValidator(regex = EMAIL_REGEX, message = SUSPICIOUS_STR)])
    date = models.DateField()
    unixStartTime = models.IntegerField()
    unixEndTime = models.IntegerField()
    accessCode = models.IntegerField()


    """/* Description:
    ** __str__ is a  built-in function that allows databse entries to be named.
    **
    ** Return:
    ** A string for the name of the database entry is returned.
    */"""
    def __str__(self):
        return "{} {} - {}".format(
                                    self.date, 
                                    self.unixStartTime, 
                                    self.unixEndTime,
                                )