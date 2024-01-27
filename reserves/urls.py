"""/* Texas A&M University
** Electronic Systems Engineering Technology
** ESET-420 Engineering Technology Capstone II
** Author: Warren Watts
** File: urls.py
** --------
** The urls.py file holds information related to the Django URL dispatcher.
** This dispatcher determines where to send requests based on URL patterns.
** For more information on the Django URL dispatcher, go to 
** https://docs.djangoproject.com/en/5.0/topics/http/urls/
*/"""



# Imports
from django.views.generic import TemplateView
from django.urls import path
from . import views



urlpatterns = [
    path("", TemplateView.as_view(template_name = "reserves/index.html"), name = "home"),
    path("form/", views.loadForm, name = "form"),
    path("form/submit", views.checkSubmit, name = "submit"),
    path("value/", views.httpReqHndlrAPI, {"id" : "value"}),
    path("reserve/", views.httpReqHndlrAPI, {"id" : "reserve"}),
    path("time/", views.httpReqHndlrAPI, {"id" : "time"})
]