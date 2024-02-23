from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class UserAdmin(UserAdmin):
    list_display = ("pk", "full_name", "username", "email")
    search_fields = (
        "username",
        "email",
    )

    def full_name(self, obj) -> str:
        if not obj:
            return ""
        return str(obj)

    full_name.short_description = "Имя Фамилия"


admin.site.register(User, UserAdmin)
