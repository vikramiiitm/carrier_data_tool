from rest_framework.serializers import ModelSerializer

from account.models import CustomUser


class UserRegistrationSerializer(ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password', 'created_by', 'modified_by')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        create_by_meta = validated_data.get('created_by')

        return user
