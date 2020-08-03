from django.urls import path

from weatherApi import views

urlpatterns = [
    path('', views.home, name='home'),
   # path('errors/', views.error404, name='404'),
]

