# myapp/serializers.py
from django.db import transaction
from rest_framework import serializers
from .models import UserProfile, Post
from myapp import models
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

User = models.User


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(label="Email", write_only=True)
    password = serializers.CharField(
        label="Password",
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            try:
                user = User.objects.get(email__exact=email)
            except User.DoesNotExist:
                user = None

            # 2. Check if the user was found AND if the password is correct
            if user is None or not user.check_password(password):
                msg = _("Invalid credentials.")
                raise serializers.ValidationError(msg, code="authorization")

            # 3. (Optional but good practice) Check if the user is active
            if not user.is_active:
                msg = _("User account is disabled.")
                raise serializers.ValidationError(msg, code="authorization")

        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code="authorization")

        # The authenticated user is stored in 'attrs'
        attrs["user"] = user
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    # email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

    class Meta:
        model = models.User
        fields = ("username", "email", "password")

    def create(self, validated_data):
        user = models.User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = UserProfile
        fields = "__all__"


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Post
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ["name", "type", "price", "image", "quantity", "id"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ["id", "image"]


class AccountSerializer(serializers.ModelSerializer):
    # user = serializers.StringRelatedField()

    class Meta:
        model = models.Account
        fields = ("id", "balance", "user")
        read_only_fields = ["user"]


class DepositSerializer(serializers.Serializer):
    depositAmount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=True
    )

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Deposit amount must be positive.")
        return value


class WithdrawelSerializer(serializers.Serializer):
    cart_Total = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=True
    )

    def validate_cart_Total(self, value):
        if value <= 0:
            raise serializers.ValidationError("withdrawel amount must be positive.")
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)

    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = models.OrderItem
        fields = ["product_id", "quantity"]


class OrdersSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)

    id = serializers.IntegerField(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = models.Order
        fields = ["id", "user", "status", "order_date", "total_price", "items"]
        read_only_fields = ["status", "total_price", "order_date"]

    def create(self, validated_data):
        order_items_data = validated_data.pop("items")

        user = self.context["request"].user
        total_price = 0

        with transaction.atomic():
            order = models.Order.objects.create(user=user, **validated_data)

            for item_data in order_items_data:
                product_id = item_data["product_id"]
                quantity = item_data["quantity"]

                try:
                    product = models.Product.objects.get(id=product_id)
                except models.Product.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Product with ID {product_id} does not exist."
                    )

                models.OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price,
                )

                total_price += product.price * quantity

            order.total_price = total_price
            order.save()

            return order
