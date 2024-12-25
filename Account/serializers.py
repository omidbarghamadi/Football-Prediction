from datetime import datetime

from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from .models import CustomUser

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    first_name = serializers.CharField(max_length=50, required=False)
    last_name = serializers.CharField(max_length=50, required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("شماره موبایل باید فقط شامل اعداد باشد.")
        if len(value) < 11:
            raise serializers.ValidationError("شماره موبایل باید حداقل 11 رقم باشد.")
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("این شماره موبایل قبلاً ثبت شده است.")
        return value

    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("این ایمیل قبلاً ثبت شده است.")
        return value

    def create(self, validated_data):
        phone_number = validated_data['phone_number']
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')
        email = validated_data.get('email', '')
        password = validated_data['password']

        # ایجاد یا بازیابی کاربر
        user, created = User.objects.get_or_create(phone_number=phone_number)

        if created:
            # بروزرسانی اطلاعات کاربر
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.set_password(password)
            user.save()

        return user


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone_number = data.get('phone_number')
        password = data.get('password')

        if not phone_number or not password:
            raise serializers.ValidationError("شماره تلفن و رمز عبور الزامی هستند.")

        # ابتدا بررسی کنید که کاربری با این شماره تلفن وجود دارد
        try:
            user = CustomUser.objects.get(phone_number=phone_number)
        except CustomUser.DoesNotExist:
            raise AuthenticationFailed("شماره تلفن یا رمز عبور نادرست است.")

        # بررسی فعال بودن کاربر
        if not user.is_active:
            raise AuthenticationFailed("این حساب کاربری غیرفعال است.")

        # بررسی رمز عبور
        if not user.check_password(password):
            raise AuthenticationFailed("شماره تلفن یا رمز عبور نادرست است.")

        user.last_login = datetime.now()
        data['user'] = user
        return data

    def create(self, validated_data):
        user = validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return {
            "token": token.key,
            "user_id": user.id,
            "score": user.score,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number,
            "last_login": user.last_login,
        }


class UpdateProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=50, required=True)
    last_name = serializers.CharField(max_length=50, required=True)
    email = serializers.EmailField(max_length=70, required=True)
    password = serializers.CharField(write_only=True, required=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'password', 'email', 'is_active']

    def update(self, instance, validated_data):
        if 'first_name' in validated_data:
            instance.first_name = validated_data['first_name']
        if 'last_name' in validated_data:
            instance.last_name = validated_data['last_name']
        if 'email' in validated_data:
            instance.email = validated_data['email']
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        return instance


class TopUsersSerializer(serializers.ModelSerializer):
    phone_number = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'phone_number', 'first_name', 'last_name', 'score')

    def get_phone_number(self, obj):
        phone_number = obj.phone_number
        if len(phone_number) >= 11:
            return phone_number[:4] + "****" + phone_number[-3:]
        return phone_number

