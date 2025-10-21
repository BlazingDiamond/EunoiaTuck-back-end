# myapp/serializers.py
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
        # gemini helped with this part
        if email and password:
            try:
                # 1. Look up the user by email using the correct User model (from get_user_model)
                user = User.objects.get(email__exact=email)
            except User.DoesNotExist:
                user = None  # User not found

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
