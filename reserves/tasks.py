from celery import shared_task
from pathlib import Path

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage



EMAIL_PNG = 'Lock_Wizards_png.png'
IMG_FILE_PATH = 'reserves/templates/reserves/static/pictures/logo/Lock_Wizards_png.png'
EMAIL_TEMPLATE = "forms/email.html"
MAIN_DIR = Path.cwd()



@shared_task
def emailHndlr(context, email):

    # Making the email.html file into a string and stripping it of the HTML tags
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
    with open(Path.joinpath(MAIN_DIR, IMG_FILE_PATH), 'rb') as imageFile:
        img = MIMEImage(imageFile.read())
        img.add_header("Content-ID", "<{}>".format(EMAIL_PNG)) # Gives the image its CID
        img.add_header("Content-Disposition", "inline", filename = EMAIL_PNG) # How the image should be displayed in the body
    
    message.attach(img)
    message.send()