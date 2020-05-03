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
    path("api/gallery/query", api.GalleryQuery.as_view()),
    path("api/image/<str:hash>/thumbnail", api.ImageThumbnail.as_view(), name="image-thumbnail"),

    re_path('css/.*', views.DistFile.as_view()),
    re_path('js/.*', views.DistFile.as_view()),
    re_path('', views.VueSinglePage.as_view()),
]

if settings.DEBUG:
    urlpatterns.insert(0, path('admin/', admin.site.urls))
