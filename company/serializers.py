from rest_framework.serializers import ModelSerializer

from company.models import Company, CompanyAddress


class AddressSerializer(ModelSerializer):

    class Meta:
        model = CompanyAddress
        fields = ('address_type', 'address_1', 'address_2', 'email', 'city', 'state', 'zip_code', 'country',
                  'phone', 'company')



class CompanySerializer(ModelSerializer):
    address = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        depth = 1
        fields = ('dot', 'name', 'legal_name', 'is_active', 'incorporation_date', 'motor_carrier_number', 'address')

