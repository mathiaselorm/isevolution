from django.contrib import admin
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from drf_yasg import openapi
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

schema_view = get_schema_view(
   openapi.Info(
      title="IS EVOLUTION TASK API",
      default_version='v1',
      description="API documentation for IS EVOLUTION TASK API",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('task_api.urls')),
    
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]


admin.site.index_title = 'Project Administration' 
admin.site.site_header = 'Mathias Task Admin'
admin.site.site_title = 'Mathias Task Admin'