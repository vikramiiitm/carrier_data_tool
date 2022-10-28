from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse, request, HttpResponseRedirect
from carrier_data_tool.utils import set_username
from . import forms
from . import models
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect

class RegisterationView(TemplateView):
    template_name = "auth/register.html"

    def post(self, request):
        data = request.POST.copy()
        username = set_username(data.get('first_name'))
        data['password'] = data.get('password1')
        form = forms.UserCreationForm(data=data)
        if form.is_valid():
            user = form.save()
            user.username = username
            user.save()
            return JsonResponse({"success": "Successfully registered"})
        else:
            return JsonResponse({"error": form.errors.as_ul()})


class LoginView(TemplateView):
    template_name = "auth/login.html"

    def post(self, request):
        data = request.POST
        print(data)
        email = data.get('email')
        password = data.get('password')
        user_obj = models.CustomUser.objects.filter(username=email) | models.CustomUser.objects.filter(
            email=email)
        user_obj = user_obj.last()
        if user_obj:
            user_auth = authenticate(username=user_obj.username, password=password)
            if not user_auth:
                return HttpResponse(0)
            else:
                login(request, user_auth)
                return HttpResponse(1)
        return HttpResponse(404)



def log_out(request):
    logout(request)
    return redirect('/')


class HomeView(TemplateView):
    template_name = "home.html"