from django.views.generic import TemplateView
from django.urls import path
from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name="reserves/index.html"), name='home'),
    path('form/', views.loadForm, name='form'),
    path('form/submit', views.checkSubmit, name='submit'),
    path('value-check', views.reservesAPI)
]