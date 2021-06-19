from .models import Income, Source
from django.shortcuts import render, redirect
from django import urls
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json
from django.http import JsonResponse



def search_income(request):
    if request.method == 'POST':
        search_str=json.loads(request.body).get('searchText')
        
        income = Income.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Income.objects.filter(
            date__istartswith=search_str, owner=request.user) | Income.objects.filter(
            descriptions__icontains=search_str, owner=request.user) | Income.objects.filter(
            source__icontains=search_str, owner=request.user)

        data = income.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login.html')
def index(request):
    source=Source.objects.all()
    income = Income.objects.filter(owner=request.user)
    paginator = Paginator(income, 5)
    page_number= request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    
    context = {
        'income': income,
        'page_obj' : page_obj,
    
       
    }
    return render(request, 'income/index.html', context)
   

def add_income(request):
    sources= Source.objects.all()
    context ={
        'sources' : sources
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)
      
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, "Amount is required")
            return render(request, 'income/add_income.html', context)

        descriptions=request.POST['description']
        date=request.POST['income_date']
        source=request.POST['source']

        if not descriptions:
            messages.error(request, 'Description is required')
            return render(request, 'income/add_income.html', context)
          

        Income.objects.create(owner=request.user, amount=amount, date=date,
                                source=source, descriptions=descriptions)
        messages.success(request, 'Income saved successfully')

        return redirect('income')


@login_required(login_url='/authentication/login')
def update_income(request, id):
    income = Income.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources': sources
    }
    if request.method == 'GET':
        return render(request, 'income/update_income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/update_income.html', context)
        descriptions = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not descriptions:
            messages.error(request, 'description is required')
            return render(request, 'income/update_income.html', context)

        income.owner = request.user
        income.amount = amount
        income.date = date
        income.source = source
        income.descriptions = descriptions

        income.save()
        messages.success(request, 'Income updated  successfully')

        return redirect('income')

@login_required(login_url='/authentication/login')
def delete_income(request, id):
    income = Income.objects.get(pk=id)
    income.delete()
    messages.success(request, 'Income has been deleted')
    return redirect('income')



