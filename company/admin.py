from django.contrib import admin
from company.models import *
# Register your models here.

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    fields = ('dba', 'legal_name', 'dot', 'is_active', 'incorporation_date', 'motor_carrier_number', 'phone')
    list_display = ('id', 'name', 'legal_name', 'dot', 'phone', 'is_active', 'incorporation_date', 'motor_carrier_number')
    search_fields = ('id','dot', 'legal_name', 'is_active')

admin.site.register(CompanyAddress)

admin.site.register(CompanyRepresentative)

@admin.register(Basics)
class BsicsAdmin(admin.ModelAdmin):
    list_display = ('company', 'basics_id')

@admin.register(OperationClasfication)
class OperationClassificationAdmin(admin.ModelAdmin):
    # fields = ('operaton_classfication_id', 'company', 'operation_classification_description')
    list_display = ('operaton_classfication_id', 'company', 'operation_classification_description')
    search_fields = ('operaton_classfication_id', 'company', 'operation_classification_description')

@admin.register(InspectionAndSafetyMeasures)
class InspectionAndSafetyMeasuresAdmin(admin.ModelAdmin):
    list_display = ('company', 'hazmat')
admin.site.register(LicensingAndInsurence)

@admin.register(CargoCarried)
class CargoCarrierAdmin(admin.ModelAdmin):
    list_display = ('company', 'description')

@admin.register(BasicsEntity)
class BasicsEntityAdmin(admin.ModelAdmin):
    list_display = ('basics', 'code')

@admin.register(InsuranceHistory)
class BasicsEntityAdmin(admin.ModelAdmin):
    list_display = ('form', 'type', 'policy_surety', 'company')

@admin.register(Crash)
class BasicsEntityAdmin(admin.ModelAdmin):
    list_display = ('crash_total', 'company')
