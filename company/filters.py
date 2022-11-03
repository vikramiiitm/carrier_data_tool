import django_filters

from company.models import Company


class CompanyFilters(django_filters.FilterSet):

    class Meta:
        model = Company
        fields = {
            'name': ['icontains'],
            'legal_name': ['icontains'],
            'dot': ['iexact'],
        }