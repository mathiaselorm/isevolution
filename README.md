# IS EVOLUTION TASK API Documentation  

## Table of Contents
1. [Project Description](#project-description)
    - [Database Schema](#database-schema)
    - [Tenant-Aware Access Control in Views](#tenant-aware-access-control-in-views)
    - [Authentication with Simple JWT](#authentication-with-simple-jwt)
2. [Setup Instructions](#setup-instructions)
    - [Prerequisites](#prerequisites)
    - [Installation Steps](#installation-steps)
3. [Accessing Swagger API Documentation](#accessing-swagger-api-documentation)
    - [Swagger UI](#swagger-ui)
    - [ReDoc](#redoc)
4. [Testing the API](#testing-the-api)
    - [Obtaining JWT Tokens](#obtaining-jwt-tokens)
    - [Using JWT Tokens for Authenticated Requests](#using-jwt-tokens-for-authenticated-requests)
5. [Quickstart](#quickstart)
6. - [Running Tests](#running-tests)
7. - [Setting Up Environment Variables](#setting-up-environment-variables)



## 1. Project Description

The IS EVOLUTION TASK API is a Django-based multi-tenant application designed to provide tenant-specific isolation for managing products. Built using Django and Django Rest Framework (DRF), the application ensures that each tenant (organization) has exclusive access to its data while offering core functionalities for user authentication, tenant-aware access control, and robust RESTful APIs for managing products. Authentication is implemented using JSON Web Tokens (JWT) via the Simple JWT library.

### Database Schema

The database schema is designed to support multi-tenancy and product management with clear relationships between the models:

#### Tenant Model:
- Represents an organization or tenant in the system.

**Relationships**:
- **One-to-Many with User**: A tenant can have multiple users.
- **One-to-Many with Product**: A tenant can have multiple products.

#### User Model:
- Extends Django's built-in user model to include tenant association.

**Relationships**:
- **Foreign Key to Tenant**: Links non-superusers to a specific tenant. Superusers are not linked to any tenant.

**Constraints**:
- Non-superusers must belong to a tenant.
- Superusers cannot belong to any tenant.

#### Product Model:
- Represents a product specific to a tenant.

**Relationships**:
- **Foreign Key to Tenant**: Links each product to a tenant, ensuring tenant-based isolation.

**Constraints**:
- Each product name is unique within a tenant.

### Tenant-Aware Access Control in Views

The application enforces tenant isolation to ensure that users can only access and manage data pertinent to their respective tenants. This is achieved through the following mechanisms:

#### Queryset Filtering

Each API view that handles data retrieval or manipulation filters the queryset based on the authenticated user's tenant. For instance, in the `ProductListCreateAPIView`, the `get_queryset` method is overridden to return only those products that belong to the current user's tenant:

```python
def get_queryset(self):
    return Product.objects.filter(tenant=self.request.user.tenant)
```

### 2. Serializer Handling

While creating a product, the `tenant` field is automatically set to the current user's tenant within the `perform_create` method, ensuring that products are always associated with the correct tenant:

```python
def perform_create(self, serializer):
    serializer.save(tenant=self.request.user.tenant)
```

### Authentication with Simple JWT

The application leverages the Simple JWT library to handle authentication via JSON Web Tokens (JWT), providing a secure and stateless authentication mechanism suitable for APIs.

#### Token Acquisition

Users obtain JWT tokens by providing valid credentials to the `/api/login/` endpoint. Upon successful authentication, an access token and a refresh token are issued.

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

### Token Usage
- Access Token: Included in the Authorization header (Bearer <access_token>) of subsequent API requests to authenticate the user.
- Refresh Token: Used to obtain a new access token when the current one expires, enhancing security by limiting the lifespan of access tokens.


## Setup Instructions
This section provides step-by-step instructions to set up and run the **IS EVOLUTION TASK API** locally.

### 2.1. Prerequisites

Ensure that the following software is installed on your local machine:

- **Python 3.8+**
- **pip** (Python package manager)
- **Git** (for cloning the repository)
- **Virtual Environment Tools** (e.g., `venv`)

### 2.2. Installation Steps

Follow the steps below to set up the project locally.

##### Step 1: Clone the Repository
Clone the project repository from GitHub to your local machine.

```bash
git clone https://github.com/mathiaselorm/isevolution.git
```
cd to the project folder (isevolution)

##### Step 2: Create and Activate a Virtual Environment
Creating a virtual environment ensures that project dependencies are isolated from other Python projects on your system.

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

##### Step 3: Install Project Dependencies
Install the required Python packages using pip.

```bash
pip install -r requirements.txt
```

#### Step 4: Apply Database Migrations
Apply the necessary database migrations to set up your database schema.

```bash
python manage.py migrate
```

#### Step 6: Create a Superuser
Create an administrative user to access the Django admin panel.

```bash
python manage.py createsuperuser
```
Follow the prompts to set up the superuser's username, email, and password.

#### Step 7: Run the Development Server
Start the Django development server to run the application locally.

```bash
python manage.py runserver
```
Access the application by navigating to http://127.0.0.1:8000/ in your web browser.


## 3. Accessing Swagger API Documentation

The **IS EVOLUTION TASK API** integrates Swagger and ReDoc for interactive API documentation. These tools allow you to explore and test API endpoints directly from your browser.

### 3.1. Swagger UI

Swagger UI provides a user-friendly interface to interact with your API's endpoints, view request and response schemas, and test API calls.

- **Access URL:** [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)

#### Features:
- **Interactive Documentation:** View all available API endpoints, methods, and expected inputs/outputs.
- **API Testing:** Send test requests directly from the UI and view responses.
- **Authentication Integration:** Easily add JWT tokens to authenticate API requests within the UI.

### 3.2. ReDoc

ReDoc offers a clean and customizable documentation interface, providing an alternative to Swagger UI.

- **Access URL:** [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)

#### Features:
- **Responsive Design:** Optimized for both desktop and mobile viewing.
- **Detailed Documentation:** Presents API specifications in a structured and readable format.
- **Ease of Navigation:** Easily navigate through different API sections and endpoints.


## 4. Testing the API

Testing the **IS EVOLUTION TASK API** involves interacting with its endpoints using tools like Postman or cURL. This section provides step-by-step instructions on authenticating and performing CRUD operations on the Product model.


### 4.1. Obtaining JWT Tokens

Before accessing secured API endpoints, you must authenticate to receive a pair of JWT tokens: an access token and a refresh token.


- **Endpoint:** `/api/login/`  
- **Method:** `POST`  
- **URL:** [http://127.0.0.1:8000/api/login/](http://127.0.0.1:8000/api/login/)  
- **Purpose:** Authenticates a user using their username and password, returning an access token (for authenticated API requests) and a refresh token (for renewing expired access tokens).  

#### Request Payload:
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

#### Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIs...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIs..."
}
```

- The access token is used for authenticating API requests.
- The refresh token is used to obtain new access tokens when the current one expires.

### 4.2. Using JWT Tokens for Authenticated Requests

Once you have obtained a JWT access token, include it in the `Authorization` header to authenticate API requests.

### Steps to Use JWT Tokens for Authenticated Requests

#### 1. Create a New Request
- Open Postman and click **New Request**.
- Set the method to the desired HTTP method (`GET`, `POST`, etc.).
- Specify the endpoint URL for the API you want to access (e.g., `http://127.0.0.1:8000/api/products/`).

#### 2. Set Authorization Token
- Navigate to the **Authorization** tab in Postman.
- From the dropdown, select **Bearer Token**.
- In the **Token** field, paste your JWT access token.

#### 3. Add Request Data (if required)
- If the request requires a body (e.g., for `POST` or `PUT` methods):
  - Navigate to the **Body** tab.
  - Select **raw** and set the format to `JSON`.
  - Provide the necessary JSON payload.

#### 4. Send the Request
- Click **Send**.

#### 5. Review the Response
- If authenticated successfully:
  - **Status:** `200 OK` or other appropriate success status.
  - **Body:** The API's response data.

#### Example
- **Authorization Tab:**
  - **Type:** Bearer Token
  - **Token:** `<access_token>`

- **Request Body (if required):**
```json
  {
      "name": "Example Product",
      "description": "A sample product",
      "price": 19.99,
      "quantity": 100
  }
```


## Key API Endpoints
| Method | Endpoint             | Description                         |
|--------|----------------------|-------------------------------------|
| GET    | /api/products/       | List all products                   |
| POST   | /api/products/       | Create a new product                |
| GET    | /api/products/{id}/  | Retrieve a specific product         |
| PUT    | /api/products/{id}/  | Update a specific product           |
|PATCH   | /api/products/{id}/  | Partially Update a specific product |
| DELETE | /api/products/{id}/  | Delete a specific product           |


The Swagger and ReDoc documentation provide all the necessary information for testing the API. They include details on what should be included in the request body, the required headers, and the expected responses for each endpoint. Simply navigate to the Swagger UI or ReDoc to explore and test the API endpoints.



## 5. Quickstart
To quickly run the application locally, follow these streamlined steps:

1. **Clone the Repository:**

```bash
    git clone https://github.com/mathiaselorm/isevolution.git
    cd isevolution
```

2. **Set Up Virtual Environment:**

```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies:**

 ```bash
    pip install -r requirements.txt
 ```

4. **Configure Environment Variables:**

 ```bash
    cp .env.example .env
```

- Open the `.env` file and replace placeholder values with your actual configurations.

5. **Apply Migrations and Create Superuser:**

```bash
    python manage.py migrate
    python manage.py createsuperuser
```

- Follow the prompts to set up the superuser's credentials.

6. **Run the Development Server:**

```bash
    python manage.py runserver
```

7. **Access the Application:**

    - **Main Site:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
    - **Admin Panel:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
    - **Swagger UI:** [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)
    - **ReDoc:** [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)


### 6. Running Tests
To ensure the application is functioning correctly, you can run the test suite:

```bash
python manage.py test
```
**The tests cover:**

- Model constraints and relationships.
- API endpoints for CRUD operations.
- Authentication flows.


### 7. Setting Up Environment Variables
Before running the project, create a `.env` file in the root directory with the following content:

```plaintext
SECRET_KEY=replace_with_a_secure_key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
### Purpose
The `.env` file stores sensitive configuration details for the project, such as the `SECRET_KEY` and `DEBUG` settings, to keep them secure and separate from the codebase.
```
### Running Without a `.env` File
If you don't create a `.env` file, the project will run with the following default settings:
- `SECRET_KEY`: `django-insecure-default-key-for-testing`
- `DEBUG`: `True`
- Database: SQLite (`db.sqlite3`)

However, it is recommended to create a `.env` file for custom configurations.