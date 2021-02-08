"""vgloss URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, re_path
from django.conf import settings

from . import views, api

urlpatterns = [
    # APIs
    path("api/action", api.Action.as_view(), name="api-action"),
    path("api/file/", api.FileListApi.as_view(), name="api-files"),
    path("api/file/<str:hash>", api.FileDetailApi.as_view(), name="api-file"),

    # Files
    path("file/<str:hash>/raw", views.FileThumbnail.as_view()),
    path("file/<str:hash>/thumbnail", views.FileThumbnail.as_view(), name="file-thumb"),

    # Static files
    re_path('css/.*', views.DistFile.as_view()),
    re_path('js/.*', views.DistFile.as_view()),
    re_path('img/.*', views.DistFile.as_view()),
    re_path('', views.VueSinglePage.as_view()),
]

if settings.DEBUG:
    urlpatterns.insert(0, path('admin/', admin.site.urls))
