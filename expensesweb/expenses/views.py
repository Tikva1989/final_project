from .models import Category, Expense
from django.shortcuts import render, redirect
from django import urls
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json
from django.http import JsonResponse, HttpResponse
import datetime
import xlwt


# Create your views here.

def search_expense(request):
    if request.method == 'POST':
        search_str=json.loads(request.body).get('searchText')
        
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            descriptions__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)

        data = expenses.values()
        return JsonResponse( list(data), safe=False)



@login_required(login_url='/authentication/login.html')
def index(request):
    categories= Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)
    page_number= request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    
    context = {
        'expenses': expenses,
        'page_obj' : page_obj,
    }
    return render(request, 'expenses/index.html', context)
   

def add_expense(request):
    categories= Category.objects.all()
    context ={
        'categories' : categories
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expenses.html', context)
      
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, "Amount is required")
            return render(request, 'expenses/add_expenses.html', context)

        descriptions=request.POST['description']
        date=request.POST['expense_date']
        category=request.POST['category']

        if not descriptions:
            messages.error(request, 'description is required')
            return render(request, 'expenses/add_expenses.html', context)
          

        Expense.objects.create(owner=request.user, amount=amount, date=date,
                                category=category, descriptions=descriptions)
        messages.success(request, 'Expense saved successfully')

        return redirect('expenses')


@login_required(login_url='/authentication/login')
def update_expense(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }
    if request.method == 'GET':
        return render(request, 'expenses/update_expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/update_expense.html', context)
        descriptions = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not descriptions:
            messages.error(request, 'description is required')
            return render(request, 'expenses/update_expense.html', context)

        expense.owner = request.user
        expense.amount = amount
        expense. date = date
        expense.category = category
        expense.descriptions = descriptions

        expense.save()
        messages.success(request, 'Expense updated  successfully')

        return redirect('expenses')

@login_required(login_url='/authentication/login')
def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense deleted')
    return redirect('expenses')

def expense_summary(request):
    today_date = datetime.date.today()
    three_months_ago = today_date- datetime.timedelta(days=30*3)
    expenses=Expense.objects.filter(owner=request.user,
                                    date__gte=three_months_ago, date__lte=today_date)
    
    finalrep = {}

    def get_category(expense):
        return expense.category
    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category= expenses.filter(category=category)

        for item in filtered_by_category:
            amount+=item.amount
        return amount
    
    for e in expenses:
        for c in category_list:
            finalrep[c]= get_expense_category_amount(c)

    return JsonResponse({'expense_category_data' : finalrep}, safe=False)


def status_view(request):
    return render(request, 'expenses/status.html')

def export_exl(request):
    response = HttpResponse(content_type= 'application/ms-excel')
    response['Content-Disposition']='attachment; filename=Expenses' + \
        str(datetime.datetime.now())+'.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')
    row_num= 0
    font_style=xlwt.XFStyle()
    font_style.font.bold = True
    
    columns = ['Amount', 'Description', 'Category', 'Date']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style=xlwt.XFStyle()
    
    rows = Expense.objects.filter(owner=request.user).values_list(
        'amount', 'descriptions', 'category', 'date')

    for row in rows:
        row_num += 1

        for col_num in range(len(row)):    
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)
    return response

