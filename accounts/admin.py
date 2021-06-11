from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import User


@admin.register(User)
class AccountAdmin(UserAdmin):
    list_display = (
        "id",
        "email",
        "username",
        "date_joined",
        "last_login",
        "is_staff",
    )
    list_display_links = ("id", "email")
    search_fields = ("email", "username")
    readonly_fields = ("date_joined", "is_staff")
