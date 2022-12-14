from allauth.account.models import EmailAddress
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.db import transaction
from rest_framework import serializers

from src.accounts.models import User


class CustomRegisterAccountSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = [
            'pk', 'first_name', 'last_name', 'username', 'email', 'password', 'password2', 'type'
        ]
        read_only_fields = [
            'type'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def save(self):
        user = User(
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
            email=self.validated_data['email'],
            username=self.validated_data['username'],
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        email = self.validated_data['email']

        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must be matched'})
        if EmailAddress.objects.filter(email=email):
            raise serializers.ValidationError({'email': 'Email is already registered'})

        user.set_password(password)
        user.save()
        return user


class CustomLoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField(style={'input_type': 'email'})
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }


class RegisterSerializerRestAPI(RegisterSerializer):
    phone_number = serializers.CharField(max_length=30)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    @transaction.atomic
    def save(self, request):
        user = super().save(request)
        print(self.data)
        user.phone_number = self.data.get('phone_number')
        # user.profile_image = self.data.get('profile_image')
        user.save()
        return user
