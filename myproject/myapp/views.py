# myapp/views.py
from django.contrib.auth import authenticate, login

from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .models import UserProfile, Post
from .serializers import (
    UserProfileSerializer,
    PostSerializer,
    RegisterSerializer,
    LoginSerializer,
)
from .models import Product
from myapp import serializers
from myapp import models
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import get_user_model


class RegisterView(generics.CreateAPIView):
    queryset = models.User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        models.Account.objects.create(user=user, balance=0.00)
        return user


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user": {
                    "id": user.pk,
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=status.HTTP_200_OK,
        )


class UserProfileListCreate(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny]


class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny]


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [AllowAny]


class ProductViewSet(viewsets.ModelViewSet):
    def get_all_products(request):
        all_products = Product.objects.all()

        context = {"products": all_products}
        return Response(request, "your_template.html", context)


class ProductsListView(generics.ListAPIView):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer
    permission_classes = [AllowAny]


class AccountViewSet(generics.ListCreateAPIView):
    permission_classes = IsAuthenticated
    # queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer

    def get_queryset(self):
        return models.Account.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
