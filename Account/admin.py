from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('id', 'phone_number', 'first_name', 'last_name', 'score', 'email',
                    'is_active', 'is_staff', 'date_joined_fa')
    list_filter = ('is_staff', 'is_active',)
    search_fields = ('phone_number', 'first_name', 'last_name', 'email')
    ordering = ('score',)

    fieldsets = (
        (None, {
            'fields': ('phone_number', 'first_name', 'last_name', 'score', 'email',
                       'password', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Read-Only Fields', {
            'fields': ('last_login',),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone_number', 'first_name', 'last_name', 'score', 'email',
                'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )

    # Read-only fields
    readonly_fields = ('last_login', 'date_joined')


admin.site.register(CustomUser, CustomUserAdmin)

