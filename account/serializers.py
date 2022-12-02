from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import ugettext_lazy as _
from account.models import CustomUser
from rest_framework.serializers import ModelSerializer, ValidationError as RestValidationError
from rest_framework.response import Response


class UserRegistrationSerializer(ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password', 'created_by', 'modified_by')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        create_by_meta = validated_data.get('created_by')

        return user

def user_can_authenticate(self, user):
    return getattr(user, 'is_active', None)

class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'username'

    def validate(self, attrs):
        user_objs = CustomUser.objects.get(username=attrs.get(self.username_field))
        print(user_objs, user_objs.username)

        if user_objs:
            password = attrs.get('password')
            print(password)

            # if not user_can_authenticate(user_objs):
            #     raise RestValidationError(detail=_('Unable to login, please contact your company administrator.'))

            credentials = {
                'username': user_objs.username,
                'password': password
            }

            if all(credentials.values()):
                user = authenticate(**credentials)
                print('authenticate user', user)
                if user is None:
                    msg = {'password': _("Please enter a valid password")}
                    raise RestValidationError(code=status.HTTP_400_BAD_REQUEST, detail=msg)

                refresh = self.get_token(user)
                print(refresh.access_token)

                data = {
                        'success': True,
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'user': user.username,
                    }
                return data