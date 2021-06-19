from django.shortcuts import render
import os
import json
from django.conf import settings
from .models import UserSettings
from django.contrib import messages


def index(request):
    currency_data = []
    f_path= os.path.join(settings.BASE_DIR, 'currencies.json')
    with open(f_path, 'r') as json_file:
        data = json.load(json_file)
        for k, v in data.items():
            currency_data.append({'name': k, 'value': v})

    exists = UserSettings.objects.filter(user=request.user).exists()
    user_settings = None
    if exists:
        user_settings = UserSettings.objects.get(user=request.user)
    if request.method == 'GET':

        return render(request, 'usersettings/index.html', {'currencies': currency_data,
                                                          'user_settings': user_settings})
    else:

        currency = request.POST['currency']
        if exists:
            user_settings.currency = currency
            user_settings.save()
        else:
            UserSettings.objects.create(user=request.user, currency=currency)
        messages.success(request, 'Changes saved')
        return render(request, 'usersettings/index.html', {'currencies': currency_data, 'user_settings': user_settings})