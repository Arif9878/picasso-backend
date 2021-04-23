"""authServer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, include
from accounts.views import AccountViewSet, change_password, client_user_list
from menu.views import MenuViewSet, MenuTypeViewSet
from accounts.views_social import oauth2_signin, oauth_keycloak_signin, detail_user
from accounts.views_login import login_view, login_admin_view, refresh_token_view
from rest_framework_jwt.views import refresh_jwt_token
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'user', AccountViewSet)
router.register(r'menu-type', MenuTypeViewSet)
router.register(r'menu', MenuViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('api/user/info', detail_user),
    path('api/user/change-password/<slug:user_id>', change_password),
    path('api/client/user/app/', client_user_list),
    path('api/token/refresh', refresh_jwt_token),
    path('api/social/google-oauth2/', oauth2_signin),
    path('api/social/keycloak-oauth/', oauth_keycloak_signin),
    path('api/auth/login/', login_view),
    path('api/auth/admin/login/', login_admin_view),
    path('api/auth/refresh/', refresh_token_view),
    path('api/menu/user/list/', MenuViewSet.as_view({ 'get': 'list'}),name='menu'),

    #Restframework
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('auth/', include('rest_framework_social_oauth2.urls')),
]
