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

    ein = models.IntegerField(null=True, blank=True)
    census_type= models.CharField(max_length=20, blank=True, null=True)
    total_driver = models.IntegerField(null=True, blank=True)
    carrier_operation = models.CharField(max_length=50, blank=True, null=True)
    common_authority_status = models.CharField(max_length=5, blank=True, null=True)
    contract_authority_status = models.CharField(max_length=5, blank=True, null=True)
    docket_number = models.CharField(max_length=15, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)


class CompanyAddress(BaseModel):
    class Address_Type_Choice(models.TextChoices):
        BILLING = 'B', _('Billing Adress')
        OFFICE = 'O', _('Office Address')

    address_type = models.CharField(max_length=20 ,choices=Address_Type_Choice.choices, default=Address_Type_Choice.BILLING, blank=True, null=True)
    address_1 = models.CharField(_('Address Line 1'), max_length=1024, blank=True, null=True)
    address_2 = models.CharField(_('Address Line 2'), max_length=1024, blank=True, null=True)
    email = models.EmailField(_('Company mail'), null=True, blank=True)
    city = models.CharField(_('City'), max_length=100)
    street = models.CharField(_('Street'), max_length=100, null=True, blank=True)
    state = models.CharField(_('State'), max_length=50)
    zip_code = models.CharField(_('Zip / Postal Code'), max_length=10)
    country = models.CharField(_('Country'), max_length=100)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='addresses')


class LicensingAndInsurence(models.Model):
    company = models.OneToOneField(Company, related_name='insurance', on_delete=models.CASCADE)
    bipdInsuranceRequired = models.CharField(max_length=5, null=True, blank=True)
    bipdInsuranceOnFile = models.IntegerField(null=True, blank=True)
    bipdRequiredAmount = models.IntegerField(null=True, blank=True)
    bondInsuranceOnFile = models.IntegerField(null=True, blank=True)
    bondInsuranceRequired = models.CharField(max_length=5, null=True, blank=True)


class OperationClasfication(models.Model):
    operaton_classfication_id = models.IntegerField()
    operation_classification_description = models.CharField(max_length=100,blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='operaton_classfication')

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

class Hazmat(models.TextChoices):
    HAZMAT = 'H', _('HAZMAT')
    NON_HAZMAT = 'N', _('NON_HAZMAT')

class InspectionAndSafetyMeasures(models.Model):

    hazmat = models.CharField(max_length=20, choices=Hazmat.choices, default=Hazmat.HAZMAT)
    inspection_total = models.IntegerField(blank=True, null=True)
    driver_inspection_total = models.IntegerField(blank=True, null=True)
    driver_oos_inspection_total = models.IntegerField(blank=True, null=True)
    vehicle_inspection_total = models.IntegerField(blank=True, null=True)
    vehicle_oos_inspection_total = models.IntegerField(blank=True, null=True)
    unsafe_driver_inspection_violation = models.IntegerField(blank=True, null=True)
    unsafe_driver_measure = models.IntegerField(blank=True, null=True)
    hos_driver_inspection_violation = models.IntegerField(blank=True, null=True)
    hos_driver_measure = models.IntegerField(blank=True, null=True)
    driver_fit_inspection_violation = models.IntegerField(blank=True, null=True)
    driver_fit_measure = models.IntegerField(blank=True, null=True)
    contr_subst_inspection_violation = models.IntegerField(blank=True, null=True)
    contr_subst_measure = models.IntegerField(blank=True, null=True)
    vehicle_maintenance_violation = models.IntegerField(blank=True, null=True)
    vehicle_maintenance_measure = models.IntegerField(blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='inspection_safety')

    class Meta:
        unique_together = ('company', 'hazmat')


class CargoCarried(models.Model):
    cargo_id = models.IntegerField()
    description = models.CharField(max_length=255, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='cargo')

# class SafetRating(models.Model):
#     safety_rating = models.Ch


class InsuranceHistory(models.Model):
    form = models.CharField(max_length=20)
    type = models.CharField(max_length=50)
    insurance_carrier = models.CharField(max_length=255, blank=True, null=True)
    policy_surety = models.CharField(max_length=100, blank=True, null=True, unique=True)
    coverage_from = models.CharField(max_length=10)
    coverage_to = models.CharField(max_length=10)
    effective_date_from = models.DateField(null=True, blank=True)
    effective_date_to = models.DateField(null=True, blank=True)
    company = models.ForeignKey(Company, related_name='insurance_history', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, null=True, blank=True)

class Crash(models.Model):
    crash_total = models.IntegerField()
    fatal_crash = models.IntegerField()
    injury_crash = models.IntegerField()
    towaway_crash = models.IntegerField()
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='crashes')