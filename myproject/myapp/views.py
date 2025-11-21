# myapp/views.py
from django.contrib.auth import authenticate, login
import json
from django.http import JsonResponse, HttpResponse
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

    def post(
        self, request, *args, **kwargs
    ):  # goes from validation to being able to see the information we need
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
            },  # this is essential for the front end as i need all the info here especially the token
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
    permission_classes = [IsAuthenticated]
    # queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer

    def get_queryset(self):
        return models.Account.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DepositView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.DepositSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        deposit_amount = serializer.validated_data["depositAmount"]

        try:
            account = models.Account.objects.get(user=self.request.user)
            account.balance += deposit_amount
            account.save()

            return Response(
                {"detail": "Deposit successful", "new_balance": account.balance},
                status=status.HTTP_200_OK,
            )
        except models.Account.DoesNotExist:
            return Response(
                {"detail": "Account not found for user."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print(f"Database error during deposit: {e}")
            return Response(
                {"detail": "An internal error occurred during the transaction."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class WithdrawelView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.WithdrawelSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart_Total = serializer.validated_data["cart_Total"]

        try:
            account = models.Account.objects.get(user=self.request.user)

            from decimal import Decimal

            withdrawal_amount = Decimal(str(cart_Total))

            if account.balance < withdrawal_amount:
                return Response(
                    {"detail": "Insufficient balance."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            account.balance -= withdrawal_amount
            account.save()

            return Response(
                {
                    "detail": "withdrawel successful",
                    "new_balance": float(account.balance),
                },
                status=status.HTTP_200_OK,
            )
        except models.Account.DoesNotExist:
            return Response(
                {"detail": "Account not found for user."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            import traceback

            print(f"Database error during withdrawel: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return Response(
                {"detail": f"An internal error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OrdersViewSet(generics.ListCreateAPIView):
    serializer_class = serializers.OrdersSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.Order.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )
