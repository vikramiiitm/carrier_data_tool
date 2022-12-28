from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer
from .models import *

class AddressSerializer(ModelSerializer):

    class Meta:
        model = CompanyAddress
        fields = ('address_type', 'address_1', 'address_2', 'email', 'city', 'state', 'zip_code', 'country',
                  'phone', 'company')

class CargoCarriedSerialzer(ModelSerializer):

    class Meta:
        model = CargoCarried
        fields = ('__all__')

class InspectionAndSafetyMeasuresSerializer(ModelSerializer):

    class Meta:
        model = InspectionAndSafetyMeasures
        fields = ('__all__')

class CompanySerializer(ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    cargo = CargoCarriedSerialzer(many=True, read_only=True)
    inspection_safety = InspectionAndSafetyMeasuresSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        # depth = 1
        fields = '__all__'
        # fields = ('dot', 'name', 'legal_name', 'is_active', 'incorporation_date', 'motor_carrier_number', 'address', 'dba')



class BasicEntitySerializer(ModelSerializer):

    class Meta:
        model = BasicsEntity
        fields = ('__all__')

class BasicSerializer(ModelSerializer):

    class Meta:
        model = Basics
        fields = ('__all__')

class OperationClasficationSerialzer(ModelSerializer):

    class Meta:
        model = OperationClasfication
        fields = ('__all__')

