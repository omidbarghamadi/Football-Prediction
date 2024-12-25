from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from jdatetime import datetime as jdatetime_datetime


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("The Phone Number field is required")
        user = self.model(phone_number=phone_number, **extra_fields)
        extra_fields.setdefault('is_active', True)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    phone_number = models.CharField(max_length=11, null=False, unique=True)
    score = models.PositiveIntegerField(default=0)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    date_joined_fa = models.CharField(max_length=25, blank=True, verbose_name="joined date")
    last_login = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.id:
            jalali_datetime = jdatetime_datetime.now()
            self.date_joined_fa = jalali_datetime.strftime("%Y/%m/%d %H:%M:%S")
        super().save(*args, **kwargs)

    def __str__(self):
        if not self.first_name and not self.last_name:
            return self.phone_number
        return f"{self.first_name} {self.last_name}"

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        db_table = 'User'
        verbose_name = "User"
        verbose_name_plural = "Users"
