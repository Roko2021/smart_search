

from django.contrib import admin
from django.urls import path
from products.views import ProductSearchAPI

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="Smart Search API",
        default_version='v1',
    ),
    public=True,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/search/', ProductSearchAPI.as_view(), name='product-search'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]
