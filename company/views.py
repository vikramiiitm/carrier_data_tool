from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView, DetailView
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import CompanyFilters
from .forms import CompanyForm
# Create your views here.
from .models import Company
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .serializers import CompanySerializer, AddressSerializer


class CreateCompany(CreateAPIView):
    serializer_class = CompanySerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            company = serializer.save()

            address = request.data.get('address')
            print(f'address: ',data)
            address['company'] = company.id
            addressserializer = AddressSerializer(data=address)
            addressserializer.is_valid(raise_exception=True)
            addressserializer.save()
            response = {
                "status" : status.HTTP_201_CREATED,
                "company": company.id,
                'address': addressserializer.data
            }

            return Response(response)

class CompanyList(LoginRequiredMixin, ListAPIView):
    serializer_class = CompanySerializer
    paginate_by = 20

    # Overriding the get_context_data method to add filtering
    def get_queryset(self):
        return Company.objects.all().order_by('dot')

    # def get_context_data(self, *args, object_list=None, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['filter'] = CompanyFilters(self.request.GET, queryset=self.get_queryset())
    #
    #     #paginate the data
    #     paginated_filtered_company = Paginator(context['filter'].qs, 10)
    #     page_number = self.request.GET.get('page')
    #     company_page_obj = paginated_filtered_company.get_page(page_number)
    #     context['company_page_obj'] = company_page_obj

        return context

class CompanyDetailView(DetailView, LoginRequiredMixin):
    model = Company
    template_name = 'company_detail.html'
    context_object_name = 'company_data'
