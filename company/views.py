from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView, DetailView

from .filters import CompanyFilters
from .forms import CompanyForm
# Create your views here.
from .models import Company
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class CreateCompany(LoginRequiredMixin, CreateView):
    template_name = 'company_data_fill.html'
    form_class = CompanyForm
    success_url = reverse_lazy('add_company')

class CompanyList(LoginRequiredMixin, ListView):
    model = Company
    template_name = 'company_list.html'
    paginate_by = 20

    # Overriding the get_context_data method to add filtering
    def get_queryset(self):
        return Company.objects.all().order_by('dot')
    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = CompanyFilters(self.request.GET, queryset=self.get_queryset())

        #paginate the data
        paginated_filtered_company = Paginator(context['filter'].qs, 10)
        page_number = self.request.GET.get('page')
        company_page_obj = paginated_filtered_company.get_page(page_number)
        context['company_page_obj'] = company_page_obj

        return context

class CompanyDetailView(DetailView, LoginRequiredMixin):
    model = Company
    template_name = 'company_detail.html'
    context_object_name = 'company_data'
