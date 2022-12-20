from django.contrib import admin
from company.models import *
# Register your models here.

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    fields = ('name', 'legal_name', 'dot', 'is_active', 'incorporation_date', 'motor_carrier_number')
    list_display = ('id', 'name', 'legal_name', 'dot', 'is_active', 'incorporation_date', 'motor_carrier_number')
    search_fields = ('dot', 'legal_name', 'is_active')

admin.site.register(CompanyAddress)

admin.site.register(CompanyRepresentative)

@admin.register(Basics)
class BsicsAdmin(admin.ModelAdmin):
    list_display = ('company', 'basics_id')

@admin.register(OperationClasfication)
class OperationClassificationAdmin(admin.ModelAdmin):
    list_display = ('operaton_classfication_id', 'company', 'operation_classification_description')

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
