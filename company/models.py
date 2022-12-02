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
    dba = models.CharField(max_length=255, blank=True, null=True)
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
    zip_code = models.CharField(_('Zip / Postal Code'), max_length=10)
    country = models.CharField(_('Country'), max_length=100)
    phone = PhoneNumberField(_('Phone Number'), blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='addresses')


class LicensingAndInsurence(models.Model):
    company = models.OneToOneField(Company, related_name='insurance', on_delete=models.CASCADE)
    # bipdInsuranceOnFile =

class OperationClasfication(models.Model):
    operaton_classfication_id = models.IntegerField()
    operation_classification_description = models.CharField(max_length=100,blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

class CompanyRepresentative(BaseModel):
    email = models.EmailField(_('Representative mail'), null=True, blank=True)
    address_1 = models.CharField(_('Address Line 1'), max_length=1024, blank=True, null=True)
    address_2 = models.CharField(_('Address Line 2'), max_length=1024, blank=True, null=True)
    city = models.CharField(_('City'), max_length=100)
    state = models.CharField(_('State'), max_length=50)
    zip_code = models.CharField(_('Zip / Postal Code'), max_length=10)
    country = models.CharField(_('Country'), max_length=100)
    phone = PhoneNumberField(_('Phone Number'), blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='representatives')


class Basics(models.Model):
    basics_id = models.IntegerField()
    percentile = models.FloatField(null=True, blank=True)
    run_date = models.DateTimeField(blank=True, null=True)
    violation_threshold = models.FloatField(blank=True,null=True)
    exceeded_fmcsa_intervention_threshold = models.FloatField(blank=True,null=True)
    measure_value = models.FloatField(blank=True, null=True)
    on_road_performance_threshold_violation_indicator = models.CharField(max_length=100, blank=True, null=True)
    serious_violation_investigation_past_12month_Indicator = models.CharField(max_length=100, blank=True, null=True)
    total_inspection_with_violation = models.IntegerField(null=True, blank=True)
    total_violation = models.IntegerField(null=True, blank=True)
    company = models.ForeignKey(Company, related_name='basics', on_delete=models.CASCADE)


class BasicsEntity(models.Model):
    code = models.CharField(max_length=100)
    code_mcmis = models.CharField(max_length=100, null=True, blank=True)
    long_description = models.CharField(max_length=100, blank=True, null=True)
    short_description = models.CharField(max_length=100, blank=True, null=True)
    basics = models.OneToOneField(Basics, on_delete=models.CASCADE, related_name='basics_entity')


class Inspection(models.Model):
    class inspection_type(models.TextChoices):
        VEHICLE = 'V', _('VEHICLE')
        DRIVER = 'D', _('DRIVER')
        HAZMAT = 'H', _('HAZMAT')

    class country(models.TextChoices):
        USA = 'U', _('USA')
        CANADA = 'C', _('CANADA')

    type = models.CharField(max_length=20, choices=inspection_type.choices)
    country = models.CharField(max_length=20, choices=country.choices, blank=True, null=True)
    Inspections = models.IntegerField(blank=True, null=True)
    oos = models.IntegerField(blank=True, null=True)
    oos_percent = models.FloatField(blank=True, null=True)
    national_average = models.FloatField(blank=True, null=True)
    company = models.ForeignKey(Company, related_name='inspection', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('type', 'company')

class CargoCarried(models.Model):
    cargo_id = models.IntegerField()
    description = models.CharField(max_length=255, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

# class SafetRating(models.Model):
#     safety_rating = models.Ch