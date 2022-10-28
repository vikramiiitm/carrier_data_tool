from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('signup/', views.RegisterationView.as_view(), name="signup"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('logout', views.log_out, name="logout"),

    path('',login_required(views.HomeView.as_view()), name="home"),


]