from django.conf import urls
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
app_name = 'company'
router = DefaultRouter()
router.register('companies', views.CompanyList, basename='company')
urlpatterns = [
    path('add-company/', views.CreateCompany.as_view(), name='add_company'),
    # path('company/<slug:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),
]
urlpatterns += router.urls