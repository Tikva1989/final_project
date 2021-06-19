from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns= [
    path('', views.index, name= 'expenses'),
    path('add_expenses/', views.add_expense, name="add_expenses"),
    path('update_expense/<int:id>', views.update_expense, name ='update_expense'),
    path('delete_expense/<int:id>', views.delete_expense, name="delete_expense"),
    path('search_expense', csrf_exempt(views.search_expense), name="search_expenses"),

    ]