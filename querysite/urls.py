from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='querysite-home'),
    path('responses/', views.responses, name='responses'),
    path('count/', views.count, name='count'),
    path('clear/', views.clear, name='clear'),
]
