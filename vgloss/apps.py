from django.contrib import admin
from django.contrib.admin.apps import AdminConfig

class CustomAdminConfig(AdminConfig):
    default_site = 'vgloss.apps.AdminSite'

class AdminSite(admin.AdminSite):
    enable_nav_sidebar = False
