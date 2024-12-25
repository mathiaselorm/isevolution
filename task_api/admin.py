from django.contrib import admin
from django.core.exceptions import PermissionDenied
from .models import Tenant, User, Product


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'address',
        'contact',
        'location',
        'created',
        'modified'
    )
    search_fields = (
        'name',
        'contact',
        'location'
    )


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'tenant',
        'is_staff',
        'is_superuser',
        'date_joined'
    )
    search_fields = (
        'username',
        'email',
        'tenant__name'
    )

    def save_model(self, request, obj, form, change):
        """
        Ensure passwords are hashed before saving a new user or updating an existing user.
        """
        if 'password' in form.changed_data:
            raw_password = obj.password
            obj.set_password(raw_password)

        super().save_model(request, obj, form, change)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'tenant',
        'price',
        'quantity',
        'created',
        'modified'
    )
    search_fields = (
        'name',
        'tenant__name'
    )
