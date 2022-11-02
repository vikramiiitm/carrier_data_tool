from django.contrib import admin
from company.models import *
# Register your models here.

admin.site.register(Company)

admin.site.register(CompanyAddress)

admin.site.register(CompanyRepresentative)
