from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView

from .filters import CompanyFilters
from .forms import CompanyForm
# Create your views here.
from .models import Company


class CreateCompany(LoginRequiredMixin, CreateView):
    template_name = 'company_data_fill.html'
    form_class = CompanyForm
    success_url = reverse_lazy('add_company')

class CompanyList(LoginRequiredMixin, ListView):
    model = Company
    template_name = 'company_list.html'

    # Overriding the get_context_data method to add filtering
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = CompanyFilters(self.request.GET, queryset=self.get_queryset())
        return context
