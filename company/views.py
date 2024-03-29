import json
from collections import OrderedDict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView, DetailView
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .filters import CompanyFilters
from .forms import CompanyForm
# Create your views here.
from .models import Company
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
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

class SmallPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 200

    def get_paginated_response(self, data):
        return Response(OrderedDict([
             ('lastPage', (self.page.paginator.count)//20+1),
             ('current', self.page.number),
             ('next', self.get_next_link()),
             ('previous', self.get_previous_link()),
             ('results', data)
         ]))


class CompanyList(ModelViewSet):
    serializer_class = CompanySerializer
    pagination_class = SmallPagination

    # Overriding the get_context_data method to add filtering
    def get_queryset(self):
        qs = self.request.query_params.dict()
        if qs:
            print('qs: ',qs)
            page = qs.pop('page', None)
            print('page: ',page)
        # if any([True for i,j in qs.items() if j]):
        #     print(123123)
        #     queryset = Company.objects.filter(
        #         Q(legal_name__contains=qs.get('legal_name') ) &
        #         # Q(name__contains=qs.get('name')) |
        #         Q(dot__contains=qs.get('dot')) &
        #         Q(addresses__city__contains=qs.get('city')))
        #     return queryset
        # else:
        return Company.objects.all().order_by('-dot')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        dot = self.request.query_params.get('dot', None)
        legal_name = self.request.query_params.get('legal_name', None)
        dba = self.request.query_params.get('dba', None)
        city = self.request.query_params.get('city', None)
        state = self.request.query_params.get('state', None)
        order_by = self.request.query_params.get('order_by')
        page_number = self.request.query_params.get('page', None)

        privateOp = self.request.query_params.get('privateOp', None)
        migrantOp = self.request.query_params.get('migrantOp', None)
        exemptOp = self.request.query_params.get('exemptOp', None)
        authorityOp = self.request.query_params.get('authorityOp', None)
        otherOp = self.request.query_params.get('otherOp', None)

        minInsp = self.request.query_params.get('minInsp', None)
        maxInsp = self.request.query_params.get('maxInsp', None)
        vehInspMin = self.request.query_params.get('vehInspMin', None)
        vehInspMax = self.request.query_params.get('vehInspMax', None)
        driverInspMin = self.request.query_params.get('driverInspMin', None)
        driverInspMax = self.request.query_params.get('driverInspMax', None)

        totalCrashMin = self.request.query_params.get('totalCrashMin', None)
        totalCrashMax = self.request.query_params.get('totalCrashMax', None)
        fatalCrashMin = self.request.query_params.get('fatalCrashMin', None)
        fatalCrashMax = self.request.query_params.get('fatalCrashMax', None)
        towawayCrashMin = self.request.query_params.get('towawayCrashMin', None)
        towawayCrashMax = self.request.query_params.get('towawayCrashMax', None)
        injuryCrashMin = self.request.query_params.get('injuryCrashMin', None)
        injuryCrashMax = self.request.query_params.get('injuryCrashMax', None)

        minDriver = self.request.query_params.get('minDriver', None)
        maxDriver = self.request.query_params.get('maxDriver', None)

        print(f'totalCrashMin: {totalCrashMin} \n totalCrashMax: {totalCrashMax} \n '
              f'fatalCrashMin: {fatalCrashMin}\nfatalCrashMax: {fatalCrashMax}\n'
              f'towawayCrashMin: {towawayCrashMin}\ntowawayCrashMax: {towawayCrashMax}\n'
              f'injuryCrashMin: {injuryCrashMin}\ninjuryCrashMax: {injuryCrashMax}')

        # cargo
        cargo = self.request.query_params.get('cargo')
        basicThreshold = self.request.query_params.get('basicThreshold')

        if order_by:
            queryset = queryset.order_by(order_by)
        if legal_name:
            queryset = queryset.filter(legal_name__icontains=legal_name)
        if dot:
            queryset = queryset.filter(dot=dot)
        if dba:
            queryset = queryset.filter(dba__icontains=dba)
        if minDriver:
            if minDriver.strip() not in ['undefined', '']:
                    queryset = queryset.filter(total_driver__gte=minDriver)
        if maxDriver:
            if maxDriver.strip() not in ['undefined', '']:
                    queryset = queryset.filter(total_driver__lte=maxDriver)
        if city:
            queryset = queryset.filter(addresses__city__icontains=city)
        if state:
            queryset = queryset.filter(addresses__state__icontains=state)


        if cargo:
            queryset = queryset.filter(cargo__description__icontains=cargo)

        if basicThreshold:
            queryset = queryset.filter(basics__total_violation__icontains='Authorized For Hire')
        # op classification
        if authorityOp:
            if authorityOp.strip() not in 'false':
                print('authority')
                queryset = queryset.filter(operaton_classfication__operation_classification_description__icontains='Authorized For Hire')
        if migrantOp:
            if migrantOp.strip() not in 'false':
                queryset = queryset.filter(operaton_classfication__operation_classification_description__icontains='Migrant')
        if exemptOp:
            if exemptOp.strip() not in 'false':
                queryset = queryset.filter(operaton_classfication__operation_classification_description__icontains='Exempt For Hire')
        if otherOp:
            if otherOp.strip() not in 'false':
                queryset = queryset.filter(operaton_classfication__operation_classification_description__icontains='Other')
        if privateOp:
            if privateOp.strip() not in 'false':
                queryset = queryset.filter(operaton_classfication__operation_classification_description__icontains='Private')

        if minInsp is not None:
            if minInsp.strip() not in ['undefined', '']:
                print('minInsp:::', minInsp)
                queryset = queryset.filter(inspection_safety__inspection_total__gte=minInsp)
        if maxInsp is not None:
            if maxInsp.strip() not in ['undefined', '']:
                queryset = queryset.filter(inspection_safety__inspection_total__lte=maxInsp)
        if vehInspMin is not None:
            if vehInspMin.strip() not in ['undefined', '']:
                queryset = queryset.filter(inspection_safety__vehicle_inspection_total__gte=vehInspMin)
        if vehInspMax is not None:
            if vehInspMax.strip() not in ['undefined', '']:
                queryset = queryset.filter(inspection_safety__vehicle_inspection_total__lte=vehInspMax)
        if driverInspMin is not None:
            if driverInspMin.strip() not in ['undefined', '']:
                queryset = queryset.filter(inspection_safety__driver_inspection_total__gte=driverInspMin)
        if driverInspMax is not None:
            if driverInspMax.strip() not in ['undefined', '']:
                queryset = queryset.filter(inspection_safety__driver_inspection_total__lte=driverInspMax)

        # crashes
        if totalCrashMin:
            if totalCrashMin.strip() not in ['undefined', '']:
                print(queryset.filter(crashes__crash_total__gte=totalCrashMin).count())
                queryset = queryset.filter(crashes__crash_total__gte=totalCrashMin)
        if totalCrashMax:
            if totalCrashMax.strip() not in ['undefined', '']:
                    queryset = queryset.filter(crashes__crash_total__lte=totalCrashMax)

        if injuryCrashMin:
            if injuryCrashMin.strip() not in ['undefined', '']:
                    queryset = queryset.filter(crashes__injury_crash__gte=injuryCrashMin)

        if injuryCrashMax:
            if injuryCrashMax.strip() not in ['undefined', '']:
                    queryset = queryset.filter(crashes__injury_crash__lte=injuryCrashMax)

        if fatalCrashMin:
            if fatalCrashMin.strip() not in ['undefined', '']:
                    queryset = queryset.filter(crashes__fatal_crash__gte=fatalCrashMin)

        if fatalCrashMax:
            if fatalCrashMax.strip() not in ['undefined', '']:
                    queryset = queryset.filter(crashes__fatal_crash__lte=fatalCrashMax)

        if towawayCrashMin:
            if towawayCrashMin.strip() not in ['undefined', '']:
                    queryset = queryset.filter(crashes__towaway_crash__gte=towawayCrashMin)

        if towawayCrashMax:
            if towawayCrashMax.strip() not in ['undefined', '']:
                    queryset = queryset.filter(crashes__towaway_crash__lte=towawayCrashMax)



        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # import pandas as pd
            # df = pd.DataFrame(serializer.data)
            # df.to_csv('company_data_from_pandas.csv')
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)
    # def get_context_data(self, *args, object_list=None, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['filter'] = CompanyFilters(self.request.GET, queryset=self.get_queryset())
    #
    #     #paginate the data
    #     paginated_filtered_company = Paginator(context['filter'].qs, 10)
    #     page_number = self.request.GET.get('page')
    #     company_page_obj = paginated_filtered_company.get_page(page_number)
    #     context['company_page_obj'] = company_page_obj

        # return context

class CompanyDetailView(APIView):
    pass
