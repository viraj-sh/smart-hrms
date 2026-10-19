"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from apps.accounts.views import (
    CustomTokenObtainPairView, 
    CustomTokenRefreshView, 
    test_auth_endpoint,
    test_admin_access,
    test_hr_access,
    test_admin_or_hr_access
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # JWT Authentication Endpoints
    path('api/auth/login', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh', CustomTokenRefreshView.as_view(), name='token_refresh'),
    
    # Test Authorization Endpoint
    path('api/auth/test', test_auth_endpoint, name='test_auth'),
    
    # Role-based Test Endpoints
    path('api/auth/test-admin', test_admin_access, name='test_admin'),
    path('api/auth/test-hr', test_hr_access, name='test_hr'),
    path('api/auth/test-admin-hr', test_admin_or_hr_access, name='test_admin_or_hr'),

    # Include dashboard URLs
    path("dashboard/", include("apps.accounts.dashboard_urls")),

    path(
    "accounts/login/",
    auth_views.LoginView.as_view(
        template_name="accounts/login.html"
    ),
    name="login",
),
path(
    "accounts/logout/",
    auth_views.LogoutView.as_view(),
    name="logout",
),
]