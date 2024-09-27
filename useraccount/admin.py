from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profiles"
    fk_name = "user"
    fieldsets = (
        (
            _("Personal Info"),
            {
                "fields": (
                    "name",
                    "address",
                    "image",
                    "about",
                    "country",
                    "company",
                    "address_line_1",
                    "headline",
                    "city",
                )
            },
        ),
    )


class UserAdmin(BaseUserAdmin):
    model = User
    list_display = (
        "email",
        "name",
        "is_staff",
        "is_superuser",
        "is_active",
        "last_login",
        "date_joined",
    )
    list_filter = ("is_superuser", "is_staff", "is_active")
    search_fields = ("email", "name")
    readonly_fields = ("date_joined", "last_login")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal Info"), {"fields": ("name", "avatar")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    inlines = (ProfileInline,)

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "full_address")
    search_fields = ("user__email", "user__name", "city", "country")
    readonly_fields = ("user",)


# Register your models with the customized admin classes
admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
