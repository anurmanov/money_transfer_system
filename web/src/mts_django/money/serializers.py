import sys
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db import transaction, IntegrityError
from rest_framework import serializers
from money.models import Currency, Course, Account, Transfer, convert_amount
from users.models import User
from users.serializers import UserSerializer

logger_info = logging.getLogger('info')

class CurrencySerializer(serializers.ModelSerializer):
    """Currency list"""
    class Meta:
        model = Currency
        fields = ['pk', 'name']

class CourseSerializer(serializers.ModelSerializer):
    """Courses list"""
    currency = CurrencySerializer()
    base_currency = CurrencySerializer()
    class Meta:
        model = Course
        fields = ['currency','base_currency','course','date']

class AccountForOwnerSerializer(serializers.ModelSerializer):
    """Owner's accounts with confidential data (balance, date of creation)"""
    created = serializers.DateTimeField(read_only=True)
    currency = CurrencySerializer()
    class Meta:
        model = Account
        fields = ['pk', 'user', 'currency', 'balance', 'created']

class AccountSerializer(serializers.ModelSerializer):
    """Regular list of accounts shows owner and currency without balance information"""
    user = UserSerializer()
    currency = CurrencySerializer()
    class Meta:
        model = Account
        fields = ['pk', 'user', 'currency']
       
class AccountCreateSerializer(serializers.Serializer):
    """Serializer for account creation"""
    currency = serializers.CharField(write_only=True, required=True)
    balance = serializers.DecimalField(max_digits=18, decimal_places=4, write_only=True, default=0)
    def validate(self, data):
        #authenticated user is account's owner
        owner = self.context['owner']
        currency_name = data.get('currency', None)
        balance_value = data.get('balance', 0)
        #check for currency existence
        try:
            currency = Currency.objects.get(name=currency_name)
        except ObjectDoesNotExist:
            return serializers.ValidationError('There is no currency "%s"' % currency_name)
        #User can not have 2 or more accounts with the same currency 
        try:
            Account.objects.get(Q(currency__name=currency_name) & Q(user=owner))
            return serializers.ValidationError('%s account is already exists!' % currency_name)
        except ObjectDoesNotExist:
            pass
        if balance_value < 0:
            return serializers.ValidationError('Bad balance value')
        data['currency'] = currency
        data['owner'] = owner
        return data
    def create(self, validated_data):
        return Account.create(validated_data['owner'], validated_data['currency'], validated_data['balance'])

class UserAccountListSerializer(serializers.ModelSerializer):
    """User's and theirs accounts"""
    accounts = AccountSerializer(many=True, read_only=True)
    class Meta:
        model = User
        fields = ['pk', 'username', 'email', 'accounts']

class TransferCreateSerializer(serializers.Serializer):
    """Serializer for transfer creation"""
    sender_account = serializers.IntegerField(write_only=True)
    receiver_account = serializers.IntegerField(write_only=True)
    amount = serializers.DecimalField(max_digits=18, decimal_places=4, default=0)
    def validate(self, data):
        #authenticated user is account's owner
        owner = self.context['owner']
        sender_account_pk = data.get('sender_account', None)
        receiver_account_pk = data.get('receiver_account', None)
        amount = data.get('amount', None)
        #all user's accounts
        owner_accounts = Account.objects.filter(user=owner)
        if owner_accounts:
            #User can not send money from other's account
            if sender_account_pk not in [account.pk for account in owner_accounts]:
                raise serializers.ValidationError('It is not yours account!')
        else:
            raise serializers.ValidationError('You do not have any accounts! Please update account list!')
        if sender_account_pk == receiver_account_pk:
            raise serializers.ValidationError('Accounts must be different')
        try:
            sender_account = Account.objects.get(pk=sender_account_pk)
        except ObjectDoesNotExist:
            raise serializers.ValidationError('There is no account with id = %s' % sender_account_pk)
        try:
            receiver_account = Account.objects.get(pk=receiver_account_pk)
        except ObjectDoesNotExist:
            raise serializers.ValidationError('There is no account with id = %s' % receiver_account_pk)
        if amount <= 0:
            raise serializers.ValidationError('Transfer amount must be greater than zero!')
        if sender_account.balance < amount:
            raise serializers.ValidationError('Unsufficient balance!')
        try:
            _, _, converted_amount = convert_amount(sender_account.currency, receiver_account.currency, amount)
        except:
            raise serializers.ValidationError(sys.exc_info()[0])
        data['sender_account'] = sender_account
        data['receiver_account'] = receiver_account
        data['converted_amount'] = converted_amount
        return data
        
    def create(self, validated_data):
        sender_account = validated_data.get('sender_account', None)
        receiver_account = validated_data.get('receiver_account', None)
        amount = validated_data.get('amount', None)
        with transaction.atomic():
            converted_amount = validated_data.get('converted_amount', None)
            #sender's balance reduced on amount
            sender_account.balance -= amount
            sender_account.save()
            #receiver's balance increased on converted_amount
            receiver_account.balance += converted_amount
            receiver_account.save()
            new_transfer = Transfer.create(sender_account, receiver_account, amount)
        return new_transfer

class TransferSerializer(serializers.ModelSerializer):
    """List of transfers"""
    sender_account = AccountSerializer()
    receiver_account = AccountSerializer()
    class Meta:
        model = Transfer
        fields = ['pk', 'sender_account', 'receiver_account', 'amount', 'created']