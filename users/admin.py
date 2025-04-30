from django.contrib import admin
from users.models import CustomUser, Notification
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Extra Info", {"fields": ("role", "bio")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Extra Info", {"fields": ("role", "bio")}),
    )
    list_display = ("username", "email", "role", "is_staff")

admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(Notification)