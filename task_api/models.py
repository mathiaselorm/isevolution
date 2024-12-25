from django.db import models
from django.contrib.auth.models import AbstractUser
from model_utils.models import TimeStampedModel
from django.core.exceptions import ValidationError


class Tenant(TimeStampedModel):
    """
    Represents a tenant or organization.
    """
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField(blank=True, null=True)
    contact = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    """
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.is_superuser and self.tenant is None:
            raise ValueError("Non-superuser users must belong to a tenant.")

        if self.is_superuser and self.tenant is not None:
            raise ValueError("Superusers should not belong to any tenant.")

        super().save(*args, **kwargs)

    def __str__(self):
        if self.tenant:
            return f"{self.username} ({self.tenant.name})"
        return f"{self.username} (Superuser)"


class Product(TimeStampedModel):
    """
    Product model that is tenant-specific.
    """
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='products'
    )
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    class Meta:
        # Ensures uniqueness of product name per tenant
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'name'],
                name='unique_product_per_tenant'
            )
        ]
        
    def clean(self):
        if Product.objects.filter(tenant=self.tenant, name=self.name).exclude(pk=self.pk).exists():
            raise ValidationError({"name": f"Product with name '{self.name}' already exists for the tenant '{self.tenant.name}'."})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.tenant.name})"
