from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.
from phonenumber_field.modelfields import PhoneNumberField

from carrier_data_tool.base_models import BaseModel


class CompanyBaseModel(models.Model):
    created_by = models.CharField(max_length=50, null=True)
    modified_by = models.CharField(max_length=50, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Company(CompanyBaseModel):
    name = models.CharField(max_length=255, blank=True, null=True)
    legal_name = models.CharField(_('Company legal name'),max_length=255)
    dot = models.IntegerField(unique=True)
    is_active = models.BooleanField(default=True)
    incorporation_date = models.DateField(_('Date of Incorporation'), blank=True, null=True)
    motor_carrier_number = models.PositiveIntegerField(null=True, blank=True, validators=(MaxValueValidator(9999999),))

class CompanyAddress(BaseModel):
    class Address_Type_Choice(models.TextChoices):
        BILLING = 'B', _('Billing Adress')
        OFFICE = 'O', _('Office Address')

    address_type = models.CharField(max_length=20 ,choices=Address_Type_Choice.choices, default=Address_Type_Choice.BILLING, blank=True, null=True)
    address_1 = models.CharField(_('Address Line 1'), max_length=1024, blank=True, null=True)
    address_2 = models.CharField(_('Address Line 2'), max_length=1024, blank=True, null=True)
    email = models.EmailField(_('Company mail'), null=True, blank=True)
    city = models.CharField(_('City'), max_length=100)
    state = models.CharField(_('State'), max_length=50)
    zip_code = models.CharField(_('Zip / Postal Code'), max_length=7)
    country = models.CharField(_('Country'), max_length=100)
    phone = PhoneNumberField(_('Phone Number'), blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='addresses')

class CompanyRepresentative(BaseModel):
    email = models.EmailField(_('Representative mail'), null=True, blank=True)
    address_1 = models.CharField(_('Address Line 1'), max_length=1024, blank=True, null=True)
    address_2 = models.CharField(_('Address Line 2'), max_length=1024, blank=True, null=True)
    city = models.CharField(_('City'), max_length=100)
    state = models.CharField(_('State'), max_length=50)
    zip_code = models.CharField(_('Zip / Postal Code'), max_length=7)
    country = models.CharField(_('Country'), max_length=100)
    phone = PhoneNumberField(_('Phone Number'), blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='representatives')

