"""newlouslist URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from allauth.account.views import logout
from allauth.socialaccount.views import signup
from django.conf import settings


urlpatterns = [
    path('', include('louslist.urls')),
    path('admin/', admin.site.urls),
    path('', include('allauth.socialaccount.providers.google.urls')),
    path("logout/", logout, name="account_logout"),
    path("social/signup/", signup, name="socialaccount_signup"),
]
