import sys
import logging
import json
from rest_framework import serializers, permissions, status 
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from money.models import Currency, Course, Account, Transfer
from money.serializers import CurrencySerializer, CourseSerializer, AccountForOwnerSerializer, AccountSerializer, TransferCreateSerializer, TransferSerializer
from users.models import User

info_logger = logging.getLogger('info')

class CurrencyListView(APIView):
    """View for getting list of currencies in the system"""
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        currency_list = Currency.objects.all()
        serializer = CurrencySerializer(currency_list, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class CourseListView(APIView):
    """View for getting list of courses of currencies in the system"""
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        course_list = Course.objects.all()
        serializer = CourseSerializer(course_list, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class AccountListForOwnerView(APIView):
    """This view is intended for owner's of the accounts.
    Owner is able to see list of its accounts with balance information,
    also owner can create new accounts.
    """
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        account_list = Account.objects.filter(user=request.user)
        serializer = AccountForOwnerSerializer(account_list, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
        
    def post(sef, request):
        serializer = AccountCreateSerializer(data=request.data, context={'owner': request.user})
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            new_account = serializer.save()
        except:
            return Response(data={'error': sys.exc_info()[0]}, status=status.HTTP_400_BAD_REQUEST)
        serializer = AccountForOwnerSerializer(new_account)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

class AccountListView(APIView):
    """Administrators of the system can see accounts of all users"""
    permission_classes = [permissions.IsAdminUser]
    def get(self, request):
        account_list = Account.objects.all().order_by('user')
        serializer = AccountSerializer(account_list, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class AccountListOfUserView(APIView):
    """View for owners of accounts and admins"""
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, pk):
        try:
            user = User.objects.get(pk=int(pk))
        except ObjectDoesNotExist:
            return Response(data={'error': 'User not found!'}, status=status.HTTP_404_NOT_FOUND)
        try:
            account_list = Account.objects.filter(user=user)
        except:
            return Response(data={'error': 'User has not accounts!'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        #Browsing balance values of the accounts is only available 
        #for admins and account's owner through AccountForOwnerSerializer view.
        if request.user == user or request.user.is_staff:
            serializer = AccountForOwnerSerializer(account_list, many=True)
        else:
            #account info without balance value for other's clients
            serializer = AccountSerializer(account_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TransferCreateView(APIView):
    """View for creating transfers"""
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        serializer = TransferCreateSerializer(data=request.data, context={'owner': request.user})
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            new_transfer = serializer.save()
        except:
            return Response(data={'error': sys.exc_info()[0]}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TransferSerializer(new_transfer)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
            
class TransferListView(APIView):
    """View for getting transfer list of current user"""
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        #all accounts of the current user
        accounts_pk = [account.pk for account in Account.objects.filter(user=request.user)]
        #all transfers of current user sorted by field "created" in descending order
        transfers = Transfer.objects.filter(sender_account__in=accounts_pk).order_by('-created')
        serializer = TransferSerializer(transfers, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)