import sys
import logging
from django.shortcuts import render
from rest_framework import authentication, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from users.models import User
from users.serializers import UserCreateSerializer, UserUpdateSerializer, UserSerializer
from money.serializers import UserAccountListSerializer

info_logger = logging.getLogger('info')

class UserListView(APIView):
    """View for getting all users"""
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        info_logger.info('UserListView')
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserAccountListView(APIView):
    """View for getting user information and its accounts"""
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, pk):
        info_logger.info('UserAccountListView')
        try:
            user = User.objects.get(pk=pk)
        except:
            return Response(data={'error': sys.exc_info()[0]}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserAccountListSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserDetailsView(APIView):
    """View for getting one particular user"""
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, pk):
        info_logger.info('UserDetailsView')
        try:
            user = User.objects.get(pk=pk)
        except:
            return Response(data={'error': sys.exc_info()[0]}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserCreateUpdateView(APIView):
    """View for creating/editing users"""
    permission_classes = [permissions.IsAdminUser]
    def post(self, request):
        """POST method for creating new user"""
        serializer = UserCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            new_user = serializer.save()
        except:
            return Response(data={'error': sys.exc_info()[0]}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(new_user)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
    def patch(self, request, pk):
        """PATCH method for editing user's name and password"""
        instance = User.objects.get(pk=pk)
        serializer = UserUpdateSerializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            new_user = serializer.save()
        except:
            return Response(data={'error': sys.exc_info()[0]}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(new_user)
        return Response(data=serializer.data, status=status.HTTP_202_ACCEPTED)