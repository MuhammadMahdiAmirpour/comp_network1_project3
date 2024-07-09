from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('start_transmitter/', views.start_transmitter, name='start_transmitter'),
    path('stop_transmitter/', views.stop_transmitter, name='stop_transmitter'),
    path('start_receiver/', views.start_receiver, name='start_receiver'),
    path('stop_receiver/', views.stop_receiver, name='stop_receiver'),
    path('get_logs/', views.get_logs, name='get_logs'),
    path('clear_logs/', views.clear_logs, name='clear_logs'),
    path('get_status/', views.get_status, name='get_status'),
]
