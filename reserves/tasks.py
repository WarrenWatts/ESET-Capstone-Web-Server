"""/* Texas A&M University
** Electronic Systems Engineering Technology
** ESET-420 Engineering Technology Capstone II
** Author: Warren Watts
** File: tasks.py
** --------
** The tasks.py file contains code related to Celery, more
** specifically for processing Django emails. Celery is a Python library 
** that creates task queues with real-time processing and task scheduling. 
** This task queue is connected to a task broker (used to transport messages in
** a task queue), which in the case of this project is Heroku Redis.
** For more information on the Celery library, go to
** https://docs.celeryq.dev/en/stable/index.html#
** For more information on Django emails, go to
** https://docs.djangoproject.com/en/5.0/topics/email/
*/"""



# Imorts for Celery
from celery import shared_task
from pathlib import Path

# Imports for Emails
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage



# Constants
EMAIL_PNG = "Lock_Wizards_png.png"
IMG_FILE_PATH = "reserves/templates/reserves/static/pictures/logo/Lock_Wizards_png.png"
EMAIL_TEMPLATE = "forms/email.html"
MAIN_DIR = Path.cwd()



"""/* Description:
** The emailHndlr() creates a shared_task (a task that is reusable by other apps)
** in Celery for generating and sending an email asynchronously. The message from
** the task will then be handled by the task broker, in this case Heroku Redis.
**
** Parameters:
** context - a dictionary containing information that will be provided in the email's message
** email - a string containing the email address to send an email to
*/"""
@shared_task
def emailHndlr(context, email):
    htmlMsg = render_to_string(EMAIL_TEMPLATE, context = context)
    plainMsg = strip_tags(htmlMsg)

    # Contents of the email
    message = EmailMultiAlternatives(
        subject = "Your Access Code",
        body = plainMsg,
        from_email = None,
        to = [email,],
    )

    message.attach_alternative(htmlMsg, "text/html")

    # Opening the Lock_Wizards_png.png image and reading it as binary
    with open(Path.joinpath(MAIN_DIR, IMG_FILE_PATH), "rb") as imageFile:
        img = MIMEImage(imageFile.read())
        img.add_header("Content-ID", "<{}>".format(EMAIL_PNG)) # Gives the image its CID
        img.add_header("Content-Disposition", "inline", filename = EMAIL_PNG) # How the image should be displayed in the body
    
    message.attach(img)
    message.send()