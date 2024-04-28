# Overview

This is the code for the full-stack web server created for my ESET Capstone team's project. The goal was to create a locally run web server that would allow the user to place a reservation for a conference room (one that would be utilizing our team's *Smart Lock Box*). Once a reservation was submitted, the user's information would be placed in a MySQL database and an email would be sent to the user containing an access code for their reservation time.

For front-end development, vanilla HTML, CSS, and Javascript were utilized, the one exception being the use of the jQuery library for its calendar. For back-end development, Django Python was used, employing both the base Django framework and the Django REST framework. Django *models* API was applied to connect to a MySQL database that stored all reservation information. In addition, the Python library Celery, in conjunction with the message broker Redis and the Platform as a Service Heroku, were employed to create asynchronous emailing.

The website was created with responsiveness in mind and is capable of running on nearly all device screens (in portrait or landscape mode), operating systems, and web browsers. (Tests were done for device screen sizes down to 320 px; for Apple, Windows, Linux, and Android operating systems; and for Safari, Google Chrome, Firefox, Brave, Edge, and Opera.)

For the *Form Page*, times are loaded to the dropdowns dynamically based on the current date, current time, and current reservations. Input validation is done on both the client-side and server-side to prevent improper data input and possible malicious actions. (This includes the assurance that reservations cannot be placed after the time has passed or if someone else placed one within that range before you.)

The Django REST API is utilized to allow the *Smart Lock Box's* ESP32 to access information from the database via HTTP POST Requests.