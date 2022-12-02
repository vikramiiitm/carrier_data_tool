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

admin.site.register(Basics)

@admin.register(OperationClasfication)
class OperationClassificationAdmin(admin.ModelAdmin):
    list_display = ('operaton_classfication_id', 'company', 'operation_classification_description')


admin.site.register(LicensingAndInsurence)

admin.site.register(CargoCarried)

admin.site.register(BasicsEntity)

admin.site.register(Inspection)