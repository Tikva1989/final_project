from django.conf.urls import url
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
import json
from django.contrib.auth.models import User
from validate_email import validate_email
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib import auth


# Create your views here.
class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email=data['email']

        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is Invalid'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'Email invalid, allready exists.'}, status=409)
        return JsonResponse({'email_valid': True})


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username=data['username']

        if not str(username).isalnum():
            return JsonResponse({'username_error': 'username should contain only alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'username invalid, allready exists. Choose another one.'}, status=409)
        return JsonResponse({'username_valid': True})

        

class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):
        #GET USER DATA
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'fields_values' : request.POST,
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) <6:
                    messages.error(request, 'Password too short')
                    return render(request, 'authentication/register.html', context)

                user = User.objects.create(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()
                # messages.success(request, 'Account Succesfully created.')
                return redirect('login' + '?message='+'Account Succesfully created.')
               

            
        return render(request, 'authentication/register.html' )


class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        username= request.POST['username']
        password= request.POST['password']
        if username and password:
            user=auth.authenticate(username=username, password=password)

            if user:
                auth.login(request, user)
                messages.success(request, "Welcome, "+user.username+' You are Logged in')
                return redirect('expenses')
                   
            messages.error(request, "Invalid credentials, try again")
            return render(request, 'authentication/login.html' )

        messages.error(request, "Please,fill in all the fields")
        return render(request, 'authentication/login.html' )
        

class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, "You are Logged out")
        return redirect('login')

        

            
        







