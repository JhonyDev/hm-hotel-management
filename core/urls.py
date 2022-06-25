"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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

from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include

from src.accounts.views import CustomRegisterAccountView, GoogleLoginView
from .settings import DEBUG, MEDIA_ROOT, MEDIA_URL


urlpatterns = [
    # ADMIN/ROOT APPLICATION
    path('admin/', admin.site.urls),

    # WEBSITE APPLICATION --------------------------------------------------------------------------------
    path('accounts/', include('src.accounts.urls', namespace='accounts')),
    path('accounts/', include('allauth.urls')),

    # REST API -------------------------------------------------------------------------------------------
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', CustomRegisterAccountView.as_view(), name='account_create_new_user'),

    path('api/', include('src.api.urls', namespace='api')),
]

if DEBUG:
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
