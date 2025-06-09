from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="WedCom API",
        default_version='v1',
        description="API documentation for WedCom project",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@wedcom.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('', include('CustomerUser.urls')),
        path('tests/', include('Test.urls')),
        path('payments/', include('Payment.urls')),
        path('courses/', include('Course.urls')),
    ],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('CustomerUser.urls')),
    path('tests/', include('Test.urls')),  # Test app URLs
    path('payments/', include('Payment.urls')),  # Payment app URLs
    path('courses/', include('Course.urls')),  # Course app URLs
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
