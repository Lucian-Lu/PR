"""
URL configuration for LAB2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('delete/<str:search_string>/', delete, name='delete'),  
    path('get/<str:search_string>/', get, name='get'),
    path('put/<str:search_string>/', put, name='put'),          
]
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('delete/<str:search_string>/', include("views.delete")),
#     path('get/<str:search_string>/', include("views.get")),
#     path('put/<str:search_string>/', include("views.put"))
# ]
