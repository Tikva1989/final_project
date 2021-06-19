from . import views
from django.urls import path

urlpatterns = [
    path('settings/', views.index, name="settings")
]