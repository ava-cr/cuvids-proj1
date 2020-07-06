from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.home, name='querysite-home'),
    path('responses/', views.responses, name='responses'),
    path('count/', views.count, name='count'),
    path('clear/', views.clear, name='clear'),
    path('generate_csv/', views.generate_csv, name='generate_csv'),
    path('redash/', views.redash, name='redash'),
]
