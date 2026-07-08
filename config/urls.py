"""
URL configuration for AI_Test_Generator project.
"""
from django.urls import path, include

urlpatterns = [
    path('', include('generator.urls')),
]
