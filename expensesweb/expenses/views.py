from django.shortcuts import render
from django import urls

# Create your views here.
def index(request):
    return render(request, 'expenses/index.html')
   

def add_expense(request):
    return render(request, 'expenses/add_expense.html')
   
    