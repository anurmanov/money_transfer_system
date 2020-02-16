import sys
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from users.models import User
from money.models import Account, Currency

info_logger = logging.getLogger('info')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'username', 'email']

class UserCreateSerializer(serializers.Serializer):
    """View for creating new user and new account"""
    username = serializers.CharField(max_length=50, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(max_length=500, write_only=True)
    balance = serializers.DecimalField(max_digits=18, decimal_places=4, default=0, write_only=True)
    currency = serializers.CharField(max_length=10, write_only=True)
    def create(self, validated_data):
        currency_name = validated_data.get('currency', None)
        balance_value = validated_data.get('balance', None)
        if currency_name:
            try:
                currency = Currency.objects.get(name=currency_name)
            except ObjectDoesNotExist:
                raise ValueError('Unknown currency')
        else:
            raise ValueError('Currency parameter is not found')
        if not balance_value:
            raise ValueError('Balance parameter is not found')
        elif balance_value < 0:
            raise ValueError('Bad balance value')
        email = validated_data.get('email', None)
        password = validated_data.get('password', None)
        username = validated_data.get('username', None)
        try:
            user = User.objects.create_user(email, password, username)
        except:
            raise Exception(sys.exc_info()[0])
        try:
            Account.create(user=user, currency=currency, balance=balance_value)
        except:
            raise Exception(sys.exc_info()[0])
        return user
    
class UserUpdateSerializer(serializers.Serializer):
    """View for updating user's credentials (username, password)"""
    email = serializers.EmailField(required=True)
    new_username = serializers.CharField(max_length=50, required=True)
    current_password = serializers.CharField(max_length=500, required=True)
    new_password = serializers.CharField(max_length=500, required=True)
    def validate(self, data):
        email =  data.get('email', None)
        new_username =  data.get('new_username', None)
        current_password =  data.get('current_password', None)
        new_password =  data.get('new_password', None)
        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            raise Exception('User %s is not found!' % email)
        current_password_encoded = user.password
        if check_password(current_password, current_password_encoded):
            validate_password(new_password)  
            if not new_username:
                raise Exception('Incorrect new username!')
        else:
            raise Exception('Incorrect password for user %s!' % user.email)  
        return data
    def update(self, instance, validated_data):
        try:
            new_username =  validated_data.get('new_username', None)
            new_password =  validated_data.get('new_password', None)
            instance.username = new_username
            instance.set_password(new_password)
            instance.save()
        except:
            raise Exception(sys.exc_info()[0])
        return instance