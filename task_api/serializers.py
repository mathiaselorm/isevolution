from rest_framework import serializers
from .models import Tenant, Product




class ProductWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for creating or updating Product objects.
    """

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'quantity']


class ProductReadSerializer(serializers.ModelSerializer):
    """
    Serializer for reading Product objects.
    """
    tenant = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'tenant',
            'name',
            'description',
            'price',
            'quantity',
            'created',
            'modified',
        ]
        read_only_fields = ['id', 'tenant', 'created', 'modified']

    def get_tenant(self, obj):
        return obj.tenant.name if obj.tenant else None
