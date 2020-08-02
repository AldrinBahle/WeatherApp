from django.urls import path

from weatherApi import views

urlpatterns = [
    path('', views.home, name='home'),
]
