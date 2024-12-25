from rest_framework.test import APITestCase
from django.test import TestCase
from django.db import IntegrityError
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Tenant, Product
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()



User = get_user_model()

class TenantModelTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Tenant A", address="123 Street", contact="123456789", location="City A")

    def test_create_tenant(self):
        tenant_count = Tenant.objects.count()
        self.assertEqual(tenant_count, 1)
        self.assertEqual(self.tenant.name, "Tenant A")
        self.assertEqual(self.tenant.address, "123 Street")

    def test_tenant_str_representation(self):
        self.assertEqual(str(self.tenant), "Tenant A")

    def test_unique_tenant_name(self):
        with self.assertRaises(IntegrityError):
            Tenant.objects.create(name="Tenant A")

class UserModelTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Tenant B")
        self.superuser = User.objects.create_superuser(username="admin", email="admin@example.com", password="password123")
        self.tenant_user = User.objects.create_user(username="user1", email="user1@example.com", password="password123", tenant=self.tenant)

    def test_create_user_with_tenant(self):
        self.assertEqual(self.tenant_user.tenant, self.tenant)
        self.assertFalse(self.tenant_user.is_superuser)

    def test_create_superuser_without_tenant(self):
        self.assertIsNone(self.superuser.tenant)
        self.assertTrue(self.superuser.is_superuser)

    def test_user_str_representation(self):
        self.assertEqual(str(self.tenant_user), "user1 (Tenant B)")
        self.assertEqual(str(self.superuser), "admin (Superuser)")

    def test_user_without_tenant_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(username="user2", email="user2@example.com", password="password123")

    def test_superuser_with_tenant_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(username="admin2", email="admin2@example.com", password="password123", tenant=self.tenant)
            

class ProductModelTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Tenant C")
        self.user = User.objects.create_user(username="user2", email="user2@example.com", password="password123", tenant=self.tenant)
        self.product = Product.objects.create(
            tenant=self.tenant,
            name="Product A",
            description="A sample product",
            price=10.99,
            quantity=100
        )

    def test_create_product(self):
        product_count = Product.objects.count()
        self.assertEqual(product_count, 1)
        self.assertEqual(self.product.name, "Product A")
        self.assertEqual(self.product.tenant, self.tenant)

    def test_product_str_representation(self):
        self.assertEqual(str(self.product), "Product A (Tenant C)")

    def test_product_unique_per_tenant(self):
        with self.assertRaises(ValidationError) as context:
            Product.objects.create(
                tenant=self.tenant,
                name="Product A",
                description="Another product",
                price=20.99,
                quantity=50
            )
        # Assert the validation error message
        self.assertIn(
            "Product with name 'Product A' already exists for the tenant 'Tenant C'.",
            context.exception.message_dict['name']
        )

    def test_product_unique_constraint_different_tenants(self):
        another_tenant = Tenant.objects.create(name="Tenant D")
        product = Product.objects.create(
            tenant=another_tenant,
            name="Product A",
            description="Another tenant's product",
            price=15.99,
            quantity=30
        )
        self.assertEqual(product.tenant, another_tenant)

        

class RelationshipsTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Tenant E")
        self.user = User.objects.create_user(username="user3", email="user3@example.com", password="password123", tenant=self.tenant)
        self.product = Product.objects.create(
            tenant=self.tenant,
            name="Product B",
            description="Another sample product",
            price=12.99,
            quantity=200
        )

    def test_user_belongs_to_tenant(self):
        self.assertEqual(self.user.tenant, self.tenant)

    def test_product_belongs_to_tenant(self):
        self.assertEqual(self.product.tenant, self.tenant)

    def test_tenant_has_users(self):
        self.assertIn(self.user, self.tenant.users.all())

    def test_tenant_has_products(self):
        self.assertIn(self.product, self.tenant.products.all())



class APITestCaseSetup(APITestCase):
    def setUp(self):
        # Create Tenants
        self.tenant1 = Tenant.objects.create(name="Tenant 1")
        self.tenant2 = Tenant.objects.create(name="Tenant 2")

        # Create Users
        self.user_tenant1 = User.objects.create_user(
            username="user1",
            password="password123",
            tenant=self.tenant1
        )
        self.user_tenant2 = User.objects.create_user(
            username="user2",
            password="password123",
            tenant=self.tenant2
        )

        # Create Products
        self.product1 = Product.objects.create(
            tenant=self.tenant1, name="Product 1", description="Description 1", price=10.00, quantity=100
        )
        self.product2 = Product.objects.create(
            tenant=self.tenant2, name="Product 2", description="Description 2", price=20.00, quantity=200
        )

        # Obtain Tokens
        self.token_user1 = RefreshToken.for_user(self.user_tenant1).access_token
        self.token_user2 = RefreshToken.for_user(self.user_tenant2).access_token

        self.auth_header_user1 = {'HTTP_AUTHORIZATION': f'Bearer {self.token_user1}'}
        self.auth_header_user2 = {'HTTP_AUTHORIZATION': f'Bearer {self.token_user2}'}


class AuthenticationFlowTest(APITestCaseSetup):
    def test_login_and_token_generation(self):
        response = self.client.post('/api/login/', {
            'username': 'user1',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_invalid_credentials(self):
        response = self.client.post('/api/login/', {
            'username': 'user1',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)


class TenantIsolationTest(APITestCaseSetup):
    def test_list_products_tenant1(self):
        response = self.client.get('/api/products/', **self.auth_header_user1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Product 1")

    def test_list_products_tenant2(self):
        response = self.client.get('/api/products/', **self.auth_header_user2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Product 2")

    def test_tenant_isolation(self):
        response = self.client.get(f'/api/products/{self.product1.id}/', **self.auth_header_user2)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProductCRUDTest(APITestCaseSetup):
    def test_create_product(self):
        data = {
            "name": "New Product",
            "description": "New Description",
            "price": 15.99,
            "quantity": 50
        }
        # First creation should succeed
        response = self.client.post('/api/products/', data, **self.auth_header_user1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], "New Product")

        # Second creation with the same name should fail
        response = self.client.post('/api/products/', data, **self.auth_header_user1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn("Product with name 'New Product' already exists", response.data['name'][0])

    def test_unique_product_name_per_tenant(self):
        data = {"name": "Product 1", "description": "Duplicate Test", "price": 5.99, "quantity": 10}
        response = self.client.post('/api/products/', data, **self.auth_header_user1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn("Product with name 'Product 1' already exists", response.data['name'][0])
    
    def test_retrieve_product(self):
        response = self.client.get(f'/api/products/{self.product1.id}/', **self.auth_header_user1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Product 1")

    def test_update_product(self):
        data = {"price": 12.99, "quantity": 150}
        response = self.client.patch(f'/api/products/{self.product1.id}/', data, **self.auth_header_user1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['price'], "12.99")
        self.assertEqual(response.data['quantity'], 150)

    def test_delete_product(self):
        response = self.client.delete(f'/api/products/{self.product1.id}/', **self.auth_header_user1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product1.id).exists())

    def test_unauthorized_access(self):
        response = self.client.post('/api/products/', {
            "name": "Unauthorized Product",
            "description": "This shouldn't be created",
            "price": 19.99,
            "quantity": 30
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
