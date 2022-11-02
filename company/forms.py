from .models import *
from django import forms

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'legal_name', 'dot', 'is_active', 'incorporation_date', 'motor_carrier_number']