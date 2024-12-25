from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from .models import Product
from .serializers import ProductReadSerializer, ProductWriteSerializer




class ProductListCreateAPIView(generics.ListCreateAPIView):
    """
    List all products or create a new products.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(tenant=self.request.user.tenant)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductReadSerializer
        return ProductWriteSerializer

    @swagger_auto_schema(
        operation_description="Retrieve all products for the logged-in user's tenant.",
        responses={200: ProductReadSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new product for the logged-in user's tenant.",
        request_body=ProductWriteSerializer,
        responses={
            201: ProductReadSerializer,
            400: "Bad Request"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Automatically set the tenant to the current user's tenant.
        """
        serializer.save(tenant=self.request.user.tenant)


class ProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a product
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(tenant=self.request.user.tenant)

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return ProductReadSerializer
        return ProductWriteSerializer

    @swagger_auto_schema(
        operation_description="Retrieve a product by ID (only if it belongs to the current tenant).",
        responses={200: ProductReadSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a product (must belong to the current tenant).",
        request_body=ProductWriteSerializer,
        responses={
            200: ProductReadSerializer,
            400: "Bad Request"
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update a product (only specified fields).",
        request_body=ProductWriteSerializer,
        responses={
            200: ProductReadSerializer,
            400: "Bad Request"
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a product from the tenant.",
        responses={
            204: "No Content",
            404: "Not Found"
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
