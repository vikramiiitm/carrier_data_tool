from django.conf import urls
from django.urls import path
from . import views

urlpatterns = [
    path('add-company/', views.CreateCompany.as_view(), name='add_company'),
    path('companies/', views.CompanyList.as_view(), name='list_company'),
    path('company/<slug:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),
]