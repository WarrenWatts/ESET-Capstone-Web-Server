# Overview

This is the code for the full-stack web server created for my ESET Capstone team's project. The goal was to create a locally run web server that would allow the user to place a reservation for a conference room (one that would be utilizing our team's *Smart Lock Box*). Once a reservation was submitted, the user's information would be placed in a MySQL database and an email would be sent to the user containing an access code for their reservation time.

For front-end development, vanilla HTML, CSS, and Javascript were utilized, the one exception being the use of the jQuery library for its calendar. For back-end development, Django Python was used, employing both the base Django framework and the Django REST framework. Django *models* API was applied to connect to a MySQL database that stored all reservation information. In addition, the Python library Celery, in conjunction with the message broker Redis and the Platform as a Service Heroku, were employed to create asynchronous emailing.

