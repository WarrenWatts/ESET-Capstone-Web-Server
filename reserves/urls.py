from django.urls import path
from . import views

urlpatterns = [
    path('', views.mainPage, name='home'),
    path('form/', views.loadForm, name='form'),
]